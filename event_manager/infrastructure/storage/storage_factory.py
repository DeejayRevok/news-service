"""
Storage factory module
"""
from event_manager.infrastructure.storage.mongo_storage import MongoStorage
from event_manager.infrastructure.storage.storage import Storage
from event_manager.infrastructure.storage.storage_type import StorageType


def storage_factory(storage_type: str, storage_config: dict) -> Storage:
    """
    Get the specified storage implementation

    Args:
        storage_type: type of the storage
        storage_config: storage configuration parameters

    Returns: configured storage implementation

    """
    if storage_type in list(map(lambda stor_type: stor_type.value, StorageType)):
        storage = StorageType[storage_type]

        if storage == StorageType.MONGO:
            return MongoStorage(**storage_config)
    else:
        raise NotImplementedError('Specified storage type not implemented')
