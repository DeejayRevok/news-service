import inspect

from uaa import models


def initialize_db(db_engine):
    for module_name, module in inspect.getmembers(models, inspect.ismodule):
        module.create_schema(db_engine)
