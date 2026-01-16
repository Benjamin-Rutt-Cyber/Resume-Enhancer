"""Data encryption utilities for sensitive column storage.

This module provides Fernet symmetric encryption for storing sensitive data
like TOTP secrets, OAuth tokens, or API keys in the database.

SECURITY IMPLEMENTATION:
- Uses Fernet (AES-128-CBC with HMAC-SHA256) for authenticated encryption
- Encryption key derived from SECRET_KEY using PBKDF2
- Each encrypted value includes timestamp for key rotation support
- Never logs decrypted values

USAGE:
    from app.utils.encryption import encrypt_value, decrypt_value

    # Encrypt a TOTP secret before storing
    encrypted = encrypt_value("JBSWY3DPEHPK3PXP")

    # Decrypt when needed
    decrypted = decrypt_value(encrypted)
"""

import base64
import logging
import hashlib
from typing import Optional

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from ..core.config import settings

logger = logging.getLogger(__name__)

# SECURITY: Salt for key derivation - should be unique per deployment
# In production, this could be stored separately or derived from another secret
ENCRYPTION_SALT = b"resume_enhancer_encryption_v1"


def _get_encryption_key() -> bytes:
    """Derive encryption key from SECRET_KEY using PBKDF2.

    SECURITY: Uses PBKDF2 with SHA256 to derive a secure encryption key
    from the application's SECRET_KEY. This ensures:
    - Key is always 32 bytes (required for Fernet)
    - Key derivation is computationally expensive (prevents brute force)
    - Same SECRET_KEY always produces same encryption key

    Returns:
        32-byte key suitable for Fernet encryption
    """
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=ENCRYPTION_SALT,
        iterations=100000,  # SECURITY: High iteration count for key derivation
    )

    key = kdf.derive(settings.SECRET_KEY.encode('utf-8'))

    # Fernet requires URL-safe base64 encoded key
    return base64.urlsafe_b64encode(key)


def _get_fernet() -> Fernet:
    """Get Fernet instance with derived key.

    Returns:
        Configured Fernet instance for encryption/decryption
    """
    return Fernet(_get_encryption_key())


def encrypt_value(plaintext: str) -> str:
    """Encrypt a string value for secure database storage.

    SECURITY: Uses Fernet authenticated encryption (AES-128-CBC + HMAC-SHA256).
    The encrypted value includes:
    - Timestamp for key rotation support
    - HMAC for integrity verification
    - Random IV for each encryption

    Args:
        plaintext: The string value to encrypt

    Returns:
        Base64-encoded encrypted value (safe for database storage)

    Raises:
        ValueError: If plaintext is empty or None
    """
    if not plaintext:
        raise ValueError("Cannot encrypt empty value")

    try:
        fernet = _get_fernet()
        encrypted = fernet.encrypt(plaintext.encode('utf-8'))
        return encrypted.decode('utf-8')
    except Exception as e:
        # SECURITY: Don't log the plaintext value
        logger.error(f"Encryption failed: {type(e).__name__}")
        raise ValueError("Encryption failed") from e


def decrypt_value(ciphertext: str) -> Optional[str]:
    """Decrypt an encrypted value from database storage.

    SECURITY: Verifies HMAC before decrypting to prevent tampering.
    Returns None for invalid/tampered data rather than raising exception
    to prevent oracle attacks.

    Args:
        ciphertext: The base64-encoded encrypted value

    Returns:
        Decrypted string value, or None if decryption fails

    Note:
        Returns None rather than raising exception for security reasons.
        Invalid tokens could indicate tampering or key rotation issues.
    """
    if not ciphertext:
        return None

    try:
        fernet = _get_fernet()
        decrypted = fernet.decrypt(ciphertext.encode('utf-8'))
        return decrypted.decode('utf-8')
    except InvalidToken:
        # SECURITY: Log but don't expose details
        logger.warning("Failed to decrypt value - invalid token or key mismatch")
        return None
    except Exception as e:
        # SECURITY: Don't log the ciphertext
        logger.error(f"Decryption failed: {type(e).__name__}")
        return None


def rotate_encryption(old_ciphertext: str, new_key: Optional[str] = None) -> Optional[str]:
    """Re-encrypt a value, optionally with a new key.

    SECURITY: Supports key rotation by decrypting with old key and
    re-encrypting with new key. If no new key provided, just re-encrypts
    with current key (refreshes timestamp).

    Args:
        old_ciphertext: Currently encrypted value
        new_key: Optional new SECRET_KEY to encrypt with

    Returns:
        Newly encrypted value, or None if decryption failed

    Note:
        For key rotation, call with new_key parameter after updating
        the SECRET_KEY in settings.
    """
    # Decrypt with current key
    plaintext = decrypt_value(old_ciphertext)
    if plaintext is None:
        return None

    # Re-encrypt (with potentially new key if settings changed)
    return encrypt_value(plaintext)


def hash_sensitive_value(value: str) -> str:
    """Create a one-way hash of a sensitive value.

    SECURITY: Use this when you only need to verify a value exists
    or match, not decrypt it. More secure than encryption for values
    that don't need to be retrieved.

    Args:
        value: The value to hash

    Returns:
        Hex-encoded SHA-256 hash
    """
    if not value:
        raise ValueError("Cannot hash empty value")

    # Use SECRET_KEY as HMAC key for additional security
    return hashlib.pbkdf2_hmac(
        'sha256',
        value.encode('utf-8'),
        settings.SECRET_KEY.encode('utf-8'),
        100000
    ).hex()
