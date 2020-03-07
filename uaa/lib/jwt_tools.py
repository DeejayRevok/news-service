import re

from jwt import decode, DecodeError, ExpiredSignatureError, encode

JWT_SECRET = 'secret'
JWT_ALGORITHM = 'HS256'


def generate_token(payload):
    return encode(payload, key=JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_token(token):
    if not re.fullmatch(r'(Bearer)\s(.*)', token):
        raise ValueError('Token is invalid')
    else:
        inner_token = re.match(r'(Bearer)\s(.*)', token)[2]
    try:
        return decode(inner_token, JWT_SECRET,
                      algorithms=[JWT_ALGORITHM])
    except (DecodeError, ExpiredSignatureError):
        raise ValueError('Token is invalid')
