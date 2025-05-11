from django.urls import path

from .views import TagDetailAPIView, TagListAPIView

urlpatterns = [
    path("tags/", TagListAPIView.as_view(), name="tag-list"),
    path("tags/<int:tag_id>/", TagDetailAPIView.as_view(), name="tag-detail"),
]
