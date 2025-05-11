from rest_core.serializers import ModelSerializer

from ..models import Tag


class TagSerializer(ModelSerializer):
    """Serializer class for Tag"""

    class Meta:
        model = Tag
        fields = ["id", "title", "color"]
        read_only_fields = ["id"]
