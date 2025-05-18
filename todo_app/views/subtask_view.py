from rest_framework.viewsets import ModelViewSet
from rest_framework.throttling import UserRateThrottle
from ..models.subtask_model import SubTask
from ..serializers.subtask_serializer import SubTaskSerializer
from rest_core.viewsets.mixins import ActionMessageMixin


class SubTaskViewSet(ActionMessageMixin, ModelViewSet):
    queryset = SubTask.objects.all()
    serializer_class = SubTaskSerializer
    throttle_classes = [UserRateThrottle]
    lookup_field = "id"