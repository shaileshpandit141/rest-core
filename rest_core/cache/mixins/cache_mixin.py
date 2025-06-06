# type: ignore[attr-defined]

import hashlib
import json
from functools import wraps
from typing import Any, Callable, Optional, TypeVar, cast

from django.core.cache import cache
from rest_framework.response import Response

F = TypeVar("F", bound=Callable[..., Any])


class CacheMixin:
    """
    A mixin for Django REST Framework ViewSets that adds caching support for:
    - list() and retrieve() actions
    - custom @action views (with decorator)
    - cache invalidation on create, update, and destroy
    """

    cache_timeout: int = 300  # Default cache timeout in seconds

    def get_cache_timeout(self) -> int:
        """Override this method to dynamically define timeout per request."""
        return self.cache_timeout

    def get_cache_key(
        self,
        action_type: str,
        pk: Optional[Any] = None,
        action_name: Optional[str] = None,
    ) -> Optional[str]:
        """
        Generate a unique cache key for various view types.

        Args:
            action_type: "list", "retrieve", "custom-list", "custom-detail"
            pk: ID for detail views
            action_name: action method name

        Returns:
            A string key or None
        """
        if action_type == "list":
            query_params = dict(sorted(self.request.query_params.items()))
            query_string = json.dumps(query_params, separators=(",", ":"))
            query_hash = hashlib.md5(query_string.encode()).hexdigest()
            return f"{self.basename}_list_{query_hash}"

        elif action_type == "retrieve" and pk is not None:
            return f"{self.basename}_detail_{pk}"

        elif action_type == "custom-list" and action_name:
            query_params = dict(sorted(self.request.query_params.items()))
            query_string = json.dumps(query_params, separators=(",", ":"))
            query_hash = hashlib.md5(query_string.encode()).hexdigest()
            return f"{self.basename}_{action_name}_list_{query_hash}"

        elif action_type == "custom-detail" and pk and action_name:
            return f"{self.basename}_{action_name}_detail_{pk}"

        return None

    def get_or_set_cache(
        self, cache_key: str, data_fn: Callable[[], Any], timeout: Optional[int] = None
    ) -> Any:
        """
        Helper to get data from cache or set it if not found.

        Args:
            cache_key: the cache key
            data_fn: function that returns data
            timeout: optional timeout in seconds

        Returns:
            Cached or computed data
        """
        data = cache.get(cache_key)
        if data is None:
            data = data_fn()
            cache.set(cache_key, data, timeout or self.get_cache_timeout())
        return data

    def invalidate_cache(
        self, pk: Optional[Any] = None, custom_actions: Optional[list[str]] = None
    ) -> None:
        """
        Invalidate caches for list/retrieve and custom actions.

        Args:
            pk: optional primary key for detail views
            custom_actions: list of custom action names to invalidate
        """
        if pk:
            key = self.get_cache_key("retrieve", pk=pk)
            if key:
                cache.delete(key)

            if custom_actions:
                for action in custom_actions:
                    key = self.get_cache_key("custom-detail", pk=pk, action_name=action)
                    if key:
                        cache.delete(key)

        # Prevent exception if not used redis.
        if hasattr(cache, "delete_pattern"):
            cache.delete_pattern(f"{self.basename}_list_*")

            if custom_actions:
                for action in custom_actions:
                    cache.delete_pattern(f"{self.basename}_{action}_list_*")

    def cache_action(
        self, detail: bool = False, action_name: Optional[str] = None
    ) -> Callable[[F], F]:
        """
        Decorator for caching @action methods.
        Works with detail=True and detail=False.

        Usage:

        @action(detail=False)
        @self.cache_action(detail=False)
        def stats(self, request): ...
        """

        def decorator(view_method: F) -> F:
            @wraps(view_method)
            def wrapper(viewset, request, *args, **kwargs) -> Response:
                name = action_name or view_method.__name__
                pk = kwargs.get("pk") if detail else None
                action_type = "custom-detail" if detail else "custom-list"
                key = viewset.get_cache_key(action_type, pk=pk, action_name=name)

                def get_data() -> None | Any:
                    response = view_method(viewset, request, *args, **kwargs)
                    return response.data if isinstance(response, Response) else response

                data = viewset.get_or_set_cache(key, get_data)
                return Response(data)

            return cast(F, wrapper)

        return decorator

    # Built-in list methods with caching
    def list(self, request, *args, **kwargs) -> Response:
        cache_key = self.get_cache_key("list")
        if not cache_key:
            return super().list(request, *args, **kwargs)

        data = self.get_or_set_cache(cache_key, lambda: self._get_list_data(request))
        return Response(data)

    def _get_list_data(self, request) -> Any:
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data).data
        else:
            serializer = self.get_serializer(queryset, many=True)
            return serializer.data

    # Built-in retrieve methods with caching
    def retrieve(self, request, *args, **kwargs) -> Response:
        pk = self.kwargs.get("pk")
        cache_key = self.get_cache_key("retrieve", pk=pk)
        if not cache_key:
            return super().retrieve(request, *args, **kwargs)

        data = self.get_or_set_cache(cache_key, lambda: self._get_detail_data())
        return Response(data)

    def _get_detail_data(self) -> Any:
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return serializer.data

    def create(self, request, *args, **kwargs) -> Response:
        response = super().create(request, *args, **kwargs)
        self.invalidate_cache()
        return response

    def update(self, request, *args, **kwargs) -> Response:
        response = super().update(request, *args, **kwargs)
        self.invalidate_cache(pk=self.kwargs.get("pk"))
        return response

    def destroy(self, request, *args, **kwargs) -> Response:
        response = super().destroy(request, *args, **kwargs)
        self.invalidate_cache(pk=self.kwargs.get("pk"))
        return response
