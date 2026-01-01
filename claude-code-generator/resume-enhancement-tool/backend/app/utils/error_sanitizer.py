"""
Error message sanitization utilities.

This module provides functions to sanitize error messages before returning them
to clients, preventing the accidental leakage of Personally Identifiable Information (PII)
such as email addresses, phone numbers, file paths, and API keys.

All detailed error information is logged server-side for debugging purposes.
"""

import re
import logging
from typing import Any

logger = logging.getLogger(__name__)


def sanitize_error_message(error: Exception, context: str = "") -> str:
    """
    Sanitize error messages to prevent PII leakage.

    This function removes potentially sensitive information from error messages
    before they are returned to clients. The full error is logged server-side
    for debugging purposes.

    Removes:
    - Email addresses → [EMAIL]
    - Phone numbers → [PHONE]
    - Absolute file paths → [PATH]
    - Workspace paths → [WORKSPACE_PATH]
    - API keys → [API_KEY]
    - UUIDs (when in paths) → [ID]

    Args:
        error: The exception object to sanitize
        context: Context description for logging (e.g., "PDF generation", "file upload")

    Returns:
        str: Sanitized error message safe for client display

    Example:
        >>> try:
        ...     open("/workspace/resumes/user@email.com/file.pdf")
        ... except Exception as e:
        ...     msg = sanitize_error_message(e, "file read")
        # Returns: "FileNotFoundError: [WORKSPACE_PATH]/[EMAIL]/file.pdf"
        # Logs: Full error with real paths for debugging
    """
    message = str(error)

    # Log the full error internally for debugging
    if context:
        logger.error(f"Error in {context}: {message}", exc_info=True)
    else:
        logger.error(f"Error: {message}", exc_info=True)

    # Remove email addresses
    message = re.sub(
        r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        '[EMAIL]',
        message
    )

    # Remove phone numbers (various formats)
    message = re.sub(
        r'\b(\+?1[-.]?)?\(?\d{3}\)?[-.]?\d{3}[-.]?\d{4}\b',
        '[PHONE]',
        message
    )

    # Remove absolute Windows paths (C:\... or D:\...)
    message = re.sub(
        r'\b[A-Za-z]:\\[^\s<>"|?*]+',
        '[PATH]',
        message
    )

    # Remove absolute Unix paths (starting with /)
    message = re.sub(
        r'/[^\s<>"|?*]+',
        '[PATH]',
        message
    )

    # Remove workspace-specific paths more explicitly
    message = re.sub(
        r'(?:workspace|resumes|jobs|enhancements)/[^\s<>"|?*]+',
        '[WORKSPACE_PATH]',
        message,
        flags=re.IGNORECASE
    )

    # Remove UUIDs when they appear in paths or IDs
    message = re.sub(
        r'\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b',
        '[ID]',
        message,
        flags=re.IGNORECASE
    )

    # Remove API keys (sk-ant-..., sk_live_..., etc.)
    message = re.sub(
        r'\b(sk[-_][a-z0-9]{4,}[-_][a-zA-Z0-9]{20,})',
        '[API_KEY]',
        message,
        flags=re.IGNORECASE
    )

    # Remove potential passwords or secrets (common patterns)
    message = re.sub(
        r'(password|secret|token|key)[\s:=]+[^\s]+',
        r'\1=[REDACTED]',
        message,
        flags=re.IGNORECASE
    )

    return message


def sanitize_dict(data: dict[str, Any], sensitive_keys: list[str] | None = None) -> dict[str, Any]:
    """
    Sanitize a dictionary by removing or masking sensitive keys.

    Useful for sanitizing request data, headers, or other structured data
    before logging or returning to clients.

    Args:
        data: Dictionary to sanitize
        sensitive_keys: List of keys to mask (defaults to common sensitive keys)

    Returns:
        dict: Sanitized copy of the dictionary

    Example:
        >>> sanitize_dict({"email": "user@example.com", "name": "John"})
        {'email': '[REDACTED]', 'name': 'John'}
    """
    if sensitive_keys is None:
        sensitive_keys = [
            'password', 'secret', 'token', 'api_key', 'apikey',
            'email', 'phone', 'ssn', 'credit_card', 'cvv'
        ]

    sanitized = data.copy()

    for key in sanitized:
        if any(sensitive in key.lower() for sensitive in sensitive_keys):
            if isinstance(sanitized[key], str) and len(sanitized[key]) > 0:
                # Show first 2 chars for debugging, mask the rest
                sanitized[key] = sanitized[key][:2] + '[REDACTED]'
            else:
                sanitized[key] = '[REDACTED]'

    return sanitized


def create_safe_error_response(
    error: Exception,
    context: str = "",
    default_message: str = "An error occurred"
) -> str:
    """
    Create a safe, generic error message for client responses.

    This function is for cases where you want to provide minimal information
    to the client while logging full details server-side.

    Args:
        error: The exception that occurred
        context: Context for logging
        default_message: Generic message to return to client

    Returns:
        str: Safe generic error message

    Example:
        >>> try:
        ...     risky_operation()
        ... except Exception as e:
        ...     msg = create_safe_error_response(e, "user operation")
        # Returns: "An error occurred"
        # Logs: Full error details including stack trace
    """
    # Log full error internally
    if context:
        logger.error(f"Error in {context}: {str(error)}", exc_info=True)
    else:
        logger.error(f"Error: {str(error)}", exc_info=True)

    # Return generic message to client
    return default_message
