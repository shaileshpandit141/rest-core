import hashlib
import json
from typing import Any, Optional

from django.core.cache import cache
from rest_framework.response import Response


class CacheMixin:
    """
    Mixin to add fully controlled caching support to DRF ViewSets.

    Features:
    - Caches `list` and `retrieve` responses automatically.
    - Cache keys include query parameters for `list`.
    - Supports cache invalidation on create/update/delete.
    - Cache timeout can be configured via `cache_timeout` attribute or
      overridden per request/action by `get_cache_timeout()`.

    Requirements:
    - Your ViewSet must be registered with a `basename` in the router for cache key generation.

    Usage:

        class ProductViewSet(CacheMixin, ModelViewSet):
            queryset = Product.objects.all()
            serializer_class = ProductSerializer
            cache_timeout = 300  # cache for 5 minutes

        # Register in urls.py with basename:
        # router.register('products', ProductViewSet, basename='product')

    """

    cache_timeout: int = 300  # default cache timeout in seconds

    def get_cache_timeout(self) -> int:
        """
        Return cache timeout in seconds.
        Override this method to customize timeout dynamically.
        """
        return self.cache_timeout

    def get_cache_key(
        self, action_type: str, pk: Optional[Any] = None
    ) -> Optional[str]:
        """
        Generate a unique cache key based on action.

        Args:
            action_type: One of "list" or "retrieve"
            pk: Primary key for retrieve action

        Returns:
            A string cache key or None if action is unsupported.
        """
        if action_type == "list":
            query_params = self.request.query_params.dict()
            query_string = json.dumps(query_params, sort_keys=True)
            query_hash = hashlib.md5(query_string.encode()).hexdigest()
            return f"{self.basename}_list_{query_hash}"

        elif action_type == "retrieve" and pk is not None:
            return f"{self.basename}_detail_{pk}"

        return None

    def list(self, request, *args, **kwargs) -> Response:
        cache_key = self.get_cache_key("list")
        if cache_key is None:
            return super().list(request, *args, **kwargs)

        data = cache.get(cache_key)
        if data is None:
            queryset = self.filter_queryset(self.get_queryset())
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                data = self.get_paginated_response(serializer.data).data
            else:
                serializer = self.get_serializer(queryset, many=True)
                data = serializer.data

            cache.set(cache_key, data, timeout=self.get_cache_timeout())

        return Response(data)

    def retrieve(self, request, *args, **kwargs) -> Response:
        pk = self.kwargs.get("pk")
        cache_key = self.get_cache_key("retrieve", pk)
        if cache_key is None:
            return super().retrieve(request, *args, **kwargs)

        data = cache.get(cache_key)
        if data is None:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            data = serializer.data
            cache.set(cache_key, data, timeout=self.get_cache_timeout())

        return Response(data)

    def create(self, request, *args, **kwargs) -> Any:
        response = super().create(request, *args, **kwargs)
        self.invalidate_cache()
        return response

    def update(self, request, *args, **kwargs) -> Any:
        response = super().update(request, *args, **kwargs)
        self.invalidate_cache(pk=self.kwargs.get("pk"))
        return response

    def destroy(self, request, *args, **kwargs) -> Any:
        response = super().destroy(request, *args, **kwargs)
        self.invalidate_cache(pk=self.kwargs.get("pk"))
        return response

    def invalidate_cache(self, pk: Optional[Any] = None) -> None:
        """
        Invalidate cached data for list and optionally detail.

        Args:
            pk: Primary key to invalidate detail cache.
            If None, only list cache invalidated.
        """
        if pk:
            key = self.get_cache_key("retrieve", pk)
            if key:
                cache.delete(key)
        # Invalidate all list caches (pattern matching)
        cache.delete_pattern(f"{self.basename}_list_*")
