from rest_core.serializers import ModelSerializer

from ..models import Todo


class TodoSerializer(ModelSerializer):
    """Serializer class for Todo"""

    class Meta:
        model = Todo
        fields = [
            "id",
            "user",
            "title",
            "description",
            "due_date",
            "completed_at",
            "priority",
            "status",
            "tags",
            "is_deleted",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
