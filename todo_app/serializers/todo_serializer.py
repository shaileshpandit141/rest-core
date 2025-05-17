from rest_framework.serializers import ModelSerializer

from rest_core.serializers.mixins import RecordsCreationMixin

from ..models import Todo
from .tag_serializer import TagSerializer
from .user_serializer import UserSerializer


class TodoSerializer(RecordsCreationMixin, ModelSerializer):
    """Serializer class for Todo"""

    # Serializer to many-to-many relationship with tags
    tags = TagSerializer(many=True, required=False)

    # Serializer to ForeginForeignKey relationship with user
    user = UserSerializer(read_only=True)

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
        read_only_fields = ["id", "user", "created_at", "updated_at"]
