from django.db import models

from .todo_model import Todo


class SubTask(models.Model):
    """Model class for SubTask"""

    class Meta:
        db_table = "sub_task"
        verbose_name = "sub task"
        verbose_name_plural = "sub tasks"
        ordering = ["-id"]

    objects = models.Manager()

    todo = models.ForeignKey(
        Todo,
        on_delete=models.CASCADE,
        primary_key=False,
        related_name="subtasks",
        related_query_name=None,
        limit_choices_to={},
        parent_link=False,
        blank=False,
        null=False,
        db_index=True,
        db_constraint=True,
        error_messages={
            "invalid": "Invalid value",
            "invalid_choice": "Select a valid choice. That choice is not one of the available choices.",
            "null": "This field cannot be null",
            "blank": "This field cannot be blank",
            "does_not_exist": "Object does not exist",
        },
    )
    title = models.CharField(
        max_length=255,
        unique=True,
        blank=False,
        null=False,
        db_index=True,
        error_messages={
            "invalid": "Invalid value",
            "null": "This field cannot be null",
            "blank": "This field cannot be blank",
            "max_length": "Ensure this value has at most 255 characters",
        },
    )
    is_done = models.BooleanField(
        default=False,
        db_index=True,
        error_messages={
            "invalid": "Invalid value",
        },
    )

    # Model fields for SubTask
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
