"""
Module which contains password management tools
"""
import hashlib


def hash_password(password: str) -> str:
    """
    Create a password hash using the blake algorithm

    Args:
        password: plain text password

    Returns: hashed password

    """
    result = hashlib.blake2b(password.encode())
    return result.hexdigest()
