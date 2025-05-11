from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

from .tag_model import Tag

User = get_user_model()


class Todo(models.Model):
    """Model class for Todo"""

    class Meta:
        db_table = "todo"
        verbose_name = "todo"
        verbose_name_plural = "todos"
        ordering = ["-id"]

    objects = models.Manager()

    PRIORITY_CHOICES = [
        ("L", "Low"),
        ("M", "Medium"),
        ("H", "High"),
        ("U", "Urgent"),
    ]

    STATUS_CHOICES = [
        ("P", "Pending"),
        ("C", "Completed"),
        ("A", "Archived"),
    ]

    # Model fields for Todo
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        primary_key=False,
        related_name="todos",
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
        unique=False,
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
    description = models.TextField(
        blank=True,
        null=True,
        db_index=False,
        default="",
        error_messages={
            "invalid": "Enter a valid value",
        },
    )
    due_date = models.DateTimeField(
        blank=True,
        null=True,
        db_index=True,
        default=None,
        error_messages={
            "invalid": "Enter a valid date/time",
        },
    )
    completed_at = models.DateTimeField(
        blank=True,
        null=True,
        db_index=True,
        default=None,
        error_messages={
            "invalid": "Enter a valid date/time",
        },
    )
    priority = models.CharField(
        max_length=255,
        unique=False,
        db_index=True,
        choices=PRIORITY_CHOICES,
        default="M",
        error_messages={
            "invalid_choice": f"Please choose one of the following options: {', '.join([f'{t[0]}: {t[-1]}' for t in PRIORITY_CHOICES])}.",
        },
    )
    status = models.CharField(
        max_length=255,
        unique=False,
        db_index=True,
        choices=STATUS_CHOICES,
        default="P",
        error_messages={
            "invalid_choice": f"Please choose one of the following options: {', '.join([f'{t[0]}: {t[-1]}' for t in STATUS_CHOICES])}."
        },
    )
    tags = models.ManyToManyField(
        Tag,
        related_name="todos",
        blank=True,
        error_messages={
            "invalid": "Invalid value",
            "invalid_choice": "Select a valid choice. That choice is not one of the available choices.",
            "invalid_pk_value": "Invalid primary key value",
            "null": "This field cannot be null",
        },
    )
    is_deleted = models.BooleanField(
        default=False,
        db_index=True,
        error_messages={
            "invalid": "Invalid value",
        },
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def mark_complete(self) -> None:
        self.status = "C"
        self.completed_at = timezone.now()
        self.save()

    def soft_delete(self) -> None:
        self.is_deleted = True
        self.save()

    def __str__(self) -> str:
        return self.title
