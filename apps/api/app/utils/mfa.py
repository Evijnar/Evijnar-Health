"""
Multi-Factor Authentication utilities.
Handles TOTP (Time-based One-Time Password) generation and verification using pyotp.
"""

import logging
import pyotp
import pyqrcode
from io import BytesIO
import base64
from typing import Tuple

logger = logging.getLogger("evijnar.mfa")


def generate_mfa_secret(user_email: str) -> Tuple[str, str]:
    """
    Generate a new TOTP secret and QR code for MFA setup.

    Args:
        user_email: User's email (used as account identifier in authenticator apps)

    Returns:
        Tuple of (secret, qr_code_base64)
        - secret: Base32-encoded secret string (user should back this up)
        - qr_code_base64: Base64-encoded PNG image of QR code
    """
    try:
        # Generate TOTP secret - pyotp.random_base32() generates a random base32 string
        secret = pyotp.random_base32()

        # Create TOTP instance with the secret
        totp = pyotp.TOTP(secret)

        # Get provisioning URI for QR code
        qr_uri = totp.provisioning_uri(name=user_email, issuer_name="Evijnar")
        qr = pyqrcode.create(qr_uri)

        # Convert QR code to base64 PNG
        png_buffer = BytesIO()
        qr.png(png_buffer, scale=8)
        png_buffer.seek(0)
        qr_code_base64 = base64.b64encode(png_buffer.getvalue()).decode()
        qr_code_data_uri = f"data:image/png;base64,{qr_code_base64}"

        logger.info(f"Generated MFA secret for {user_email}")
        return secret, qr_code_data_uri

    except Exception as e:
        logger.error(f"Failed to generate MFA secret: {str(e)}")
        raise ValueError(f"MFA generation failed: {str(e)}")


def verify_mfa_code(secret: str, code: str, time_window: int = 1) -> bool:
    """
    Verify a TOTP code against a secret.

    Args:
        secret: Base32-encoded TOTP secret
        code: 6-digit code from authenticator app
        time_window: Window of time steps (default 1 = 30-sec window)

    Returns:
        True if code is valid, False otherwise
    """
    try:
        totp = pyotp.TOTP(secret)
        # Verify with tolerance to account for clock skew
        # time_window=1 means ±30 seconds tolerance
        return totp.verify(code, valid_window=time_window)
    except Exception as e:
        logger.warning(f"MFA code verification failed: {str(e)}")
        return False


def get_provisioning_uri(secret: str, user_email: str) -> str:
    """
    Get the provisioning URI for manual entry (if QR code scan fails).

    Args:
        secret: TOTP secret
        user_email: User's email

    Returns:
        provisioning URI string (otpauth://...)
    """
    totp = pyotp.TOTP(secret)
    return totp.provisioning_uri(name=user_email, issuer_name="Evijnar")


def generate_backup_codes(count: int = 8) -> list[str]:
    """
    Generate backup codes for account recovery (if authenticator app is lost).

    Args:
        count: Number of backup codes to generate (default 8)

    Returns:
        List of backup codes
    """
    import secrets
    # Generate random 8-character alphanumeric codes
    codes = ["".join(secrets.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789") for _ in range(8)) for _ in range(count)]
    return codes
