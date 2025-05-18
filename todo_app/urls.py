from django.urls import path, re_path
from rest_framework.routers import DefaultRouter

from .views import (
    TagDetailAPIView,
    TagListAPIView,
    TodoDetailAPIView,
    TodoListAPIView,
    TodoModelChoiceAPIView,
)
from .views.subtask_view import SubTaskViewSet

# Create a router and register our viewset with it.
router = DefaultRouter()

router.register(r"subtasks", SubTaskViewSet, basename="subtask")

urlpatterns = [
    # path("tags/", TagListAPIView.as_view(), name="tag-list"),
    re_path(r"^tags/?$", TagListAPIView.as_view()),
    path("tags/<int:tag_id>/", TagDetailAPIView.as_view(), name="tag-detail"),
    path("todos/", TodoListAPIView.as_view(), name="todo-list"),
    path("todos/choice-fields/", TodoModelChoiceAPIView.as_view(), name="todo-choices"),
    path("todos/<int:todo_id>/", TodoDetailAPIView.as_view(), name="todo-detail"),
]


urlpatterns += router.urls
