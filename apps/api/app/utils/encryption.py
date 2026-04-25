"""
Encryption utilities for sensitive data.
Handles symmetric encryption/decryption of MFA secrets and other sensitive fields.
Uses Fernet (symmetric key cryptography) for simplicity and security.
"""

import logging
from typing import Optional

from cryptography.fernet import Fernet, InvalidToken
from app.config import settings

logger = logging.getLogger("evijnar.encryption")


def _get_cipher(key: str) -> Fernet:
    """
    Create a Fernet cipher from a key string.

    Args:
        key: Encryption key (must be base64-encoded 32 bytes)

    Returns:
        Fernet cipher object
    """
    try:
        return Fernet(key.encode() if isinstance(key, str) else key)
    except Exception as e:
        logger.error(f"Failed to create cipher: {str(e)}")
        raise ValueError("Invalid encryption key format")


def encrypt_data(data: str, key: Optional[str] = None) -> str:
    """
    Encrypt plaintext data using Fernet (symmetric encryption).

    Args:
        data: Plaintext data to encrypt
        key: Encryption key (default: encryption_key_patient_data from config)

    Returns:
        Base64-encoded encrypted data

    Raises:
        ValueError: If encryption fails
    """
    if key is None:
        key = settings.encryption_key_patient_data

    try:
        cipher = _get_cipher(key)
        encrypted = cipher.encrypt(data.encode() if isinstance(data, str) else data)
        return encrypted.decode()  # Return as string
    except Exception as e:
        logger.error(f"Encryption failed: {str(e)}")
        raise ValueError(f"Encryption failed: {str(e)}")


def decrypt_data(encrypted_data: str, key: Optional[str] = None) -> str:
    """
    Decrypt Fernet-encrypted data.

    Args:
        encrypted_data: Base64-encoded encrypted data
        key: Encryption key (default: encryption_key_patient_data from config)

    Returns:
        Decrypted plaintext data

    Raises:
        ValueError: If decryption fails (tampered data, wrong key, etc.)
    """
    if key is None:
        key = settings.encryption_key_patient_data

    try:
        cipher = _get_cipher(key)
        decrypted = cipher.decrypt(
            encrypted_data.encode() if isinstance(encrypted_data, str) else encrypted_data
        )
        return decrypted.decode()
    except InvalidToken:
        logger.warning("Invalid token or tampered data detected")
        raise ValueError("Decryption failed: Invalid data or tampered")
    except Exception as e:
        logger.error(f"Decryption failed: {str(e)}")
        raise ValueError(f"Decryption failed: {str(e)}")


# For MFA secrets specifically
def encrypt_mfa_secret(secret: str) -> str:
    """Encrypt MFA secret for storage"""
    return encrypt_data(secret, settings.encryption_key_patient_data)


def decrypt_mfa_secret(encrypted_secret: str) -> str:
    """Decrypt MFA secret from storage"""
    return decrypt_data(encrypted_secret, settings.encryption_key_patient_data)
