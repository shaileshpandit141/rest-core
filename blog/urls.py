from django.urls import path

from .views import BlogPostListAPIView

urlpatterns = [
    path("blog-posts/", BlogPostListAPIView.as_view(), name="blog-posts"),
]
