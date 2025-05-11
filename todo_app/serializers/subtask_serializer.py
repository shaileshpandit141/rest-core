from rest_core.serializers import ModelSerializer

from ..models import SubTask


class SubTaskSerializer(ModelSerializer):
    """Serializer class for SubTask"""

    class Meta:
        model = SubTask
        fields = ["id", "todo", "title", "is_done", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]
