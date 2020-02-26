"""
Storage factory module
"""
from infrastructure.storage.mongo_storage import MongoStorage
from infrastructure.storage.storage import Storage
from infrastructure.storage.storage_type import StorageType


def storage_factory(storage_type: str, storage_config: dict) -> Storage:
    """
    Get the specified storage implementation

    Args:
        storage_type: type of the storage
        storage_config: storage configuration parameters

    Returns: configured storage implementation

    """
    assert storage_type in list(
        map(lambda stor_type: stor_type.value, StorageType)), 'Specified storage type not implemented'

    storage = StorageType[storage_type]

    if storage == StorageType.MONGO:
        return MongoStorage(**storage_config)
