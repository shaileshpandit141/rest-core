from rest_framework.serializers import ModelSerializer as DrfModelSerializer
from rest_framework.serializers import Serializer as DrfSerializer

from .mixins import RecordsCreationMixin


class Serializer(RecordsCreationMixin, DrfSerializer):
    """
    A custom serializer class that extends Django REST Framework's Serializer.

    This class incorporates the following mixins:
    - RecordsCreationMixin: Provides utilities for creating records.

    Use this class when you need a base serializer with additional features
    provided by the included mixins.
    """

    pass


class ModelSerializer(RecordsCreationMixin, DrfModelSerializer):
    """
    A custom model serializer class that extends Django REST Framework's ModelSerializer.

    This class incorporates the following mixins:
    - RecordsCreationMixin: Provides utilities for creating records.

    Use this class when you need a model serializer with additional features
    provided by the included mixins.
    """

    pass
