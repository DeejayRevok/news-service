"""
Authentication module
"""
from uaa.lib.jwt_tools import decode_token, generate_token
from uaa.lib.pass_tools import hash_password
from uaa.services.users_service import UserService


class AuthService:
    """
    Authentication service
    """
    JWT_SECRET = 'secret'
    JWT_ALGORITHM = 'HS256'

    def __init__(self, user_service: UserService):
        """
        Initialize the authentication service

        Args:
            user_service: User service used to authenticate the users
        """
        self._user_service = user_service

    async def authenticate(self, username: str, password: str) -> dict:
        """
        Authenticate the user with the specified password. If the authentication is successful,
        return the authentication token.

        Args:
            username: username to authenticate
            password: user access password

        Returns: authentication token

        """
        user = await self._user_service.get_user_by_name(username)
        if user is not None:
            pass_hash = hash_password(password)
            if user.password == pass_hash:
                payload = {
                    'user_id': user.id,
                }
                jwt_token = generate_token(payload)
                return {'token': jwt_token.decode('utf-8')}
            else:
                raise ValueError('Wrong credentials')
        else:
            raise ValueError('Wrong credentials')

    async def validate_token(self, token: str):
        """
        Validate the authentication token

        Args:
            token: token to authenticate

        Returns: authenticated token data

        """
        payload = decode_token(token)
        try:
            user_identifier = payload['user_id']
        except KeyError:
            raise ValueError('Token is invalid')

        user = await self._user_service.get_user_by_id(user_identifier)
        if user is not None:
            return user
        else:
            raise ValueError('Invalid user')
