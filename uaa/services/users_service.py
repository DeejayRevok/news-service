"""
Users service module
"""
from uaa.infrastructure.storage.sql_storage import SqlStorage
from uaa.lib.pass_tools import hash_password
from uaa.models.user import User


class UserService:
    """
    User service implementation
    """
    def __init__(self, client: SqlStorage):
        """
        Initialize the service with the specified database client

        Args:
            client: database client
        """
        self._client = client

    async def create_user(self, username: str, password: str) -> User:
        """
        Create a new user

        Args:
            username: user name
            password: user password

        Returns: user model created

        """
        password_hash = hash_password(password)
        return self._client.save(User(username=username, password=password_hash))

    async def get_user_by_id(self, identifier: int) -> User:
        """
        Get an user by its identifier

        Args:
            identifier: user identifier to get

        Returns: queried user

        """
        return self._client.get_one(User, id=identifier)

    async def get_user_by_name(self, username: str) -> User:
        """
        Gets an user by its name

        Args:
            username: user name to get

        Returns: queried user

        """
        return self._client.get_one(User, username=username)
