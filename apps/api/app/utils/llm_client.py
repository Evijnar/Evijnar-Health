# apps/api/app/utils/llm_client.py
"""
Claude API wrapper for intelligent data mapping.
Includes caching, retry logic, and structured output parsing.
"""

import json
import hashlib
import logging
import asyncio
from typing import Optional, Dict, Any, Any as CallableReturnType
import redis.asyncio as redis

from anthropic import Anthropic, AsyncAnthropic
from anthropic import APIError, RateLimitError, APIConnectionError
from app.config import settings

logger = logging.getLogger("evijnar.llm")


class LLMCache:
    """Redis-backed cache for LLM responses"""

    def __init__(self, redis_url: Optional[str] = None):
        self.redis_url = redis_url or settings.redis_url if hasattr(settings, 'redis_url') else "redis://localhost:6379"
        self.redis: Optional[redis.Redis] = None
        self.enabled = self.redis_url is not None

    async def connect(self):
        """Initialize Redis connection"""
        if not self.enabled:
            return

        try:
            self.redis = await aioredis.from_url(self.redis_url)
            await self.redis.ping()
            logger.info("Connected to Redis cache")
        except Exception as e:
            logger.warning(f"Failed to connect to Redis: {e}. Continuing without cache.")
            self.enabled = False

    async def disconnect(self):
        """Close Redis connection"""
        if self.redis:
            await self.redis.close()

    def _get_cache_key(self, prompt: str, model: str) -> str:
        """Generate deterministic cache key from prompt"""
        prompt_hash = hashlib.sha256(prompt.encode()).hexdigest()[:16]
        return f"llm:v1:{model}:{prompt_hash}"

    async def get(self, prompt: str, model: str) -> Optional[Dict[str, Any]]:
        """Get cached response"""
        if not self.enabled or not self.redis:
            return None

        try:
            key = self._get_cache_key(prompt, model)
            cached = await self.redis.get(key)
            if cached:
                logger.debug(f"Cache hit for: {key[:20]}...")
                return json.loads(cached)
        except Exception as e:
            logger.warning(f"Cache retrieval error: {e}")

        return None

    async def set(self, prompt: str, model: str, response: Dict[str, Any], ttl: int = 86400):
        """Cache response with TTL"""
        if not self.enabled or not self.redis:
            return

        try:
            key = self._get_cache_key(prompt, model)
            await self.redis.setex(key, ttl, json.dumps(response))
            logger.debug(f"Cached response: {key[:20]}...")
        except Exception as e:
            logger.warning(f"Cache write error: {e}")


class ClaudeClient:
    """
    Async wrapper around Anthropic's Claude API.
    Handles structured output parsing, retries, and caching.
    """

    def __init__(self, api_key: Optional[str] = None, cache: Optional[LLMCache] = None):
        self.api_key = api_key or settings.anthropic_api_key if hasattr(settings, 'anthropic_api_key') else None
        self.client = AsyncAnthropic(api_key=self.api_key)
        self.cache = cache or LLMCache()
        self.model = "claude-opus-4"  # Use latest model
        self.max_retries = 3
        self.retry_delay = 1  # seconds

        self.usage_stats = {
            "total_calls": 0,
            "total_tokens": 0,
            "total_cached": 0,
            "estimated_cost_usd": 0.0,
        }

        # Token pricing (as of 2026, may vary)
        self.pricing = {
            "input_tokens_per_mtok": 0.003,      # $0.003 per 1M input tokens
            "output_tokens_per_mtok": 0.015,     # $0.015 per 1M output tokens
        }

        logger.info(f"Claude client initialized with model: {self.model}")

    async def initialize(self):
        """Initialize cache connection"""
        await self.cache.connect()

    async def shutdown(self):
        """Clean up resources"""
        await self.cache.disconnect()

    async def call_claude(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        response_format: Optional[str] = "json",  # "json" or "text"
        temperature: float = 0.3,  # Lower for structured tasks
        max_tokens: int = 1024,
        cache_ttl: int = 86400,
    ) -> Dict[str, Any]:
        """
        Call Claude API with structured output.

        Args:
            prompt: User prompt
            system_prompt: System context
            response_format: "json" or "text"
            temperature: Model temperature (0-1)
            max_tokens: Max tokens in response
            cache_ttl: Cache TTL in seconds

        Returns:
            Parsed response as dict

        Raises:
            LLMError: If API call fails
        """
        try:
            # Check cache first
            cached_response = await self.cache.get(prompt, self.model)
            if cached_response:
                self.usage_stats["total_cached"] += 1
                return cached_response

            # Build messages
            messages = [{"role": "user", "content": prompt}]

            # Add JSON format instruction
            if response_format == "json":
                if system_prompt:
                    system_prompt += "\n\nAlways respond with valid JSON."
                else:
                    system_prompt = "Always respond with valid JSON."

            # Retry logic
            for attempt in range(self.max_retries):
                try:
                    logger.debug(f"Claude API call (attempt {attempt + 1}/{self.max_retries})")

                    response = await self.client.messages.create(
                        model=self.model,
                        max_tokens=max_tokens,
                        temperature=temperature,
                        system=system_prompt,
                        messages=messages,
                    )

                    # Extract text content
                    response_text = response.content[0].text

                    # Update usage stats
                    self.usage_stats["total_calls"] += 1
                    self.usage_stats["total_tokens"] += response.usage.input_tokens + response.usage.output_tokens

                    # Calculate cost
                    input_cost = (response.usage.input_tokens / 1_000_000) * self.pricing["input_tokens_per_mtok"]
                    output_cost = (response.usage.output_tokens / 1_000_000) * self.pricing["output_tokens_per_mtok"]
                    self.usage_stats["estimated_cost_usd"] += input_cost + output_cost

                    logger.debug(
                        f"Claude response: {len(response_text)} chars, "
                        f"tokens: {response.usage.input_tokens + response.usage.output_tokens}"
                    )

                    # Parse JSON if needed
                    if response_format == "json":
                        try:
                            # Extract JSON from response (may have markdown code blocks)
                            if "```json" in response_text:
                                json_str = response_text.split("```json")[1].split("```")[0].strip()
                            elif "```" in response_text:
                                json_str = response_text.split("```")[1].split("```")[0].strip()
                            else:
                                json_str = response_text

                            parsed_response = json.loads(json_str)
                        except json.JSONDecodeError as e:
                            logger.error(f"Failed to parse Claude JSON response: {str(e)}")
                            logger.error(f"Response text: {response_text[:200]}...")
                            raise ValueError(f"Invalid JSON in Claude response: {str(e)}")
                    else:
                        parsed_response = {"text": response_text}

                    # Cache the response
                    await self.cache.set(prompt, self.model, parsed_response, cache_ttl)

                    return parsed_response

                except RateLimitError:
                    if attempt < self.max_retries - 1:
                        wait_time = self.retry_delay * (2 ** attempt)  # Exponential backoff
                        logger.warning(f"Rate limited. Waiting {wait_time}s before retry...")
                        await asyncio.sleep(wait_time)
                    else:
                        raise APIError("Rate limit exceeded after retries", request=None)

                except APIConnectionError as e:
                    if attempt < self.max_retries - 1:
                        wait_time = self.retry_delay * (2 ** attempt)
                        logger.warning(f"Connection error: {e}. Waiting {wait_time}s before retry...")
                        await asyncio.sleep(wait_time)
                    else:
                        raise

        except Exception as e:
            logger.error(f"Claude API error: {str(e)}")
            raise

    def get_usage_stats(self) -> Dict[str, Any]:
        """Get accumulated usage statistics"""
        return self.usage_stats.copy()

    def reset_usage_stats(self):
        """Reset usage statistics"""
        self.usage_stats = {
            "total_calls": 0,
            "total_tokens": 0,
            "total_cached": 0,
            "estimated_cost_usd": 0.0,
        }


# Global instance
_llm_client: Optional[ClaudeClient] = None


async def get_llm_client() -> ClaudeClient:
    """Get or create global Claude client"""
    global _llm_client

    if _llm_client is None:
        _llm_client = ClaudeClient()
        await _llm_client.initialize()

    return _llm_client


async def shutdown_llm_client():
    """Shutdown global Claude client"""
    global _llm_client

    if _llm_client:
        await _llm_client.shutdown()
        _llm_client = None
