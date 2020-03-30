"""
aiohttp class routes table definition module
"""
import inspect
from typing import Any

from aiohttp.web_routedef import RouteTableDef, _Deco


class ClassRouteTableDef(RouteTableDef):
    """
    Class route table definition implementation
    """
    def __repr__(self) -> str:
        """
        Get the route table string representation

        Returns: string representation

        """
        return "<ClassRouteTableDef count={}>".format(len(self._items))

    def clean_routes(self):
        """
        Clean all the routes from the table
        """
        self._items = list()

    def route(self,
              method: str,
              path: str,
              **kwargs: Any) -> _Deco:
        """
        Create a new route definition

        Args:
            method: method associated to the route
            path: path of the route
            **kwargs: additional route addition arguments

        Returns: route function execution result

        """
        def inner(handler: Any) -> Any:
            handler.route_info = (method, path, kwargs)
            return handler
        return inner

    def add_class_routes(self, instance: Any) -> None:
        """
        Add the routes of the specified instance to the route table

        Args:
            instance: instance to search routes

        """
        def predicate(member: Any) -> bool:
            return all((inspect.iscoroutinefunction(member),
                        hasattr(member, "route_info")))
        for _, handler in inspect.getmembers(instance, predicate):
            method, path, kwargs = handler.route_info
            super().route(method, path, **kwargs)(handler)
