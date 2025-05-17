from django.contrib.auth import get_user_model
from rest_framework.serializers import ModelSerializer

from rest_core.serializers.mixins import RecordsCreationMixin

User = get_user_model()


class UserSerializer(RecordsCreationMixin, ModelSerializer):
    """Serializer class for User"""

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
        ]
        read_only_fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
        ]
