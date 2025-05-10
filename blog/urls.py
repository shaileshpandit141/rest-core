from django.urls import path

from .views import BlogPostDetailAPIView, BlogPostListAPIView

urlpatterns = [
    path("blog-posts/", BlogPostListAPIView.as_view(), name="blog-posts"),
    path(
        "blog-posts/<int:blog_post_id>/",
        BlogPostDetailAPIView.as_view(),
        name="blog-post-detail",
    ),
]
