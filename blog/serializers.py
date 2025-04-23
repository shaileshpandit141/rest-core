from rest_framework import serializers

from .models import BlogPost


class BlogPostSerializer(serializers.ModelSerializer):
    """Serializer class for BlogPost"""

    class Meta:
        model = BlogPost
        fields = [
            "id",
            "title",
            "slug",
            "owner",
            "content",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "slug", "owner", "created_at", "updated_at"]
