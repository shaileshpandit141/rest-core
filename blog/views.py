from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.throttling import UserRateThrottle
from rest_framework.views import APIView

from blog.models import BlogPost
from blog.serializers import BlogPostSerializer
from rest_core.response import Response

User = get_user_model()

owner = User.objects.get(username="shailesh")


class BlogPostListAPIView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [UserRateThrottle]

    def get(self, request) -> Response:
        instance = BlogPost.objects.all()
        serializer = BlogPostSerializer(instance=instance, many=True)
        return Response(
            message="Blog post retrive successful",
            data=serializer.data,
            status=status.HTTP_200_OK,
        )

    def post(self, request) -> Response:
        serializer = BlogPostSerializer(
            data=request.data, many=isinstance(request.data, list)
        )

        if serializer.is_valid():
            serializer.save(owner=owner)
            return Response(
                message="Blog post create successful",
                data=serializer.data,
                status=status.HTTP_200_OK,
            )

        return Response(
            message="Blog post create not successful",
            data=serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )
