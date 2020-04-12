"""
Module which contains jwt token management functions
"""
import os
import re

from jwt import decode, DecodeError, ExpiredSignatureError, encode

JWT_SECRET_KEY = 'JWT_SECRET'
JWT_ALGORITHM = 'HS256'


def generate_token(payload: dict) -> bytes:
    """
    Generate one JWT token containing the payload data

    Args:
        payload: payload to encode

    Returns: JWT token

    """
    jwt_secret = os.environ.get(JWT_SECRET_KEY, None)
    if jwt_secret is not None:
        return encode(payload, key=jwt_secret, algorithm=JWT_ALGORITHM)
    else:
        raise ValueError('JWT secret not defined')


def decode_token(token: str) -> dict:
    """
    Decode the input JWT token

    Args:
        token: token to decode

    Returns: payload encoded in the token

    """
    if not re.fullmatch(r'(Bearer)\s(.*)', token):
        raise ValueError('Token is invalid')

    inner_token = re.match(r'(Bearer)\s(.*)', token)[2]

    jwt_secret = os.environ.get(JWT_SECRET_KEY, None)
    if jwt_secret is not None:
        try:
            return decode(inner_token, jwt_secret,
                          algorithms=[JWT_ALGORITHM])
        except (DecodeError, ExpiredSignatureError):
            raise ValueError('Token is invalid')
    else:
        raise ValueError('JWT secret not defined')
