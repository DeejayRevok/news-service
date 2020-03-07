import hashlib


def hash_password(password):
    result = hashlib.blake2b(password.encode())
    return result.hexdigest()
