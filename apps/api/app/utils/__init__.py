"""
Utilities package for Evijnar API.
Contains helpers for authentication, encryption, MFA, and LLM integration.
"""

from .auth import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    verify_token,
    extract_token_payload,
    get_user_id_from_token,
    get_user_role_from_token,
)
from .encryption import (
    encrypt_data,
    decrypt_data,
    encrypt_mfa_secret,
    decrypt_mfa_secret,
)
from .mfa import (
    generate_mfa_secret,
    verify_mfa_code,
    get_provisioning_uri,
    generate_backup_codes,
)

__all__ = [
    # Auth utilities
    "hash_password",
    "verify_password",
    "create_access_token",
    "create_refresh_token",
    "verify_token",
    "extract_token_payload",
    "get_user_id_from_token",
    "get_user_role_from_token",
    # Encryption utilities
    "encrypt_data",
    "decrypt_data",
    "encrypt_mfa_secret",
    "decrypt_mfa_secret",
    # MFA utilities
    "generate_mfa_secret",
    "verify_mfa_code",
    "get_provisioning_uri",
    "generate_backup_codes",
]
