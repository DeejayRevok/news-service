from uaa.infrastructure.storage.sql_storage import SqlStorage
from uaa.lib.pass_tools import hash_password
from uaa.models.user import User


class UserService:

    def __init__(self, client: SqlStorage):
        self._client = client

    async def create_user(self, username, password):
        password_hash = hash_password(password)
        return self._client.save(User(username=username, password=password_hash))

    async def get_user_by_id(self, identifier):
        return self._client.get(User, id=identifier)

    async def get_user_by_name(self, username):
        return self._client.get(User, username=username)
