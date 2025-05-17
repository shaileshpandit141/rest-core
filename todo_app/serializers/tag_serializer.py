from rest_framework.serializers import ModelSerializer

from rest_core.serializers.mixins import RecordsCreationMixin

from ..models import Tag


class TagSerializer(RecordsCreationMixin, ModelSerializer):
    """Serializer class for Tag"""

    class Meta:
        model = Tag
        fields = ["id", "title", "color"]
        read_only_fields = ["id"]
