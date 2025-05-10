from rest_framework.serializers import ModelSerializer as DrfModelSerializer
from rest_framework.serializers import Serializer as DrfSerializer

from .mixins import FileUrlMixin, RecordsCreationMixin


class Serializer(FileUrlMixin, RecordsCreationMixin, DrfSerializer):
    """
    A custom serializer class that extends Django REST Framework's Serializer.

    This class incorporates the following mixins:
    - FileUrlMixin: Adds functionality for handling file URLs.
    - RecordsCreationMixin: Provides utilities for creating records.

    Use this class when you need a base serializer with additional features
    provided by the included mixins.
    """

    pass


class ModelSerializer(FileUrlMixin, RecordsCreationMixin, DrfModelSerializer):
    """
    A custom model serializer class that extends Django REST Framework's ModelSerializer.

    This class incorporates the following mixins:
    - FileUrlMixin: Adds functionality for handling file URLs.
    - RecordsCreationMixin: Provides utilities for creating records.

    Use this class when you need a model serializer with additional features
    provided by the included mixins.
    """

    pass
