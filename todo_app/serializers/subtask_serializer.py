from rest_framework.serializers import ModelSerializer

from rest_core.serializers.mixins import RecordsCreationMixin

from ..models import SubTask


class SubTaskSerializer(RecordsCreationMixin, ModelSerializer):
    """Serializer class for SubTask"""

    class Meta:
        model = SubTask
        fields = ["id", "todo", "title", "is_done", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]
