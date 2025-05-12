from django.urls import path

from .views import TagDetailAPIView, TagListAPIView, TodoDetailAPIView, TodoListAPIView

urlpatterns = [
    path("tags/", TagListAPIView.as_view(), name="tag-list"),
    path("tags/<int:tag_id>/", TagDetailAPIView.as_view(), name="tag-detail"),
    path("todos/", TodoListAPIView.as_view(), name="todo-list"),
    path("todos/<int:todo_id>/", TodoDetailAPIView.as_view(), name="todo-detail"),
]
