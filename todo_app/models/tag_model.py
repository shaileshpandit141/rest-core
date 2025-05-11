from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Tag(models.Model):
    """Model class for Tag"""

    class Meta:
        db_table = "tag"
        verbose_name = "tag"
        verbose_name_plural = "tags"
        ordering = ["-id"]

    objects = models.Manager()

    # Model fields for Tag
    title = models.CharField(
        max_length=50,
        unique=True,
        null=False,
        blank=False,
        db_index=True,
        error_messages={
            "invalid": "Invalid value",
            "null": "This field cannot be null",
            "blank": "This field cannot be blank",
            "max_length": "Ensure this value has at most 50 characters",
        },
    )
    color = models.CharField(
        max_length=8,
        unique=False,
        null=True,
        blank=True,
        db_index=False,
        default="#cccccc",
        error_messages={
            "invalid": "Invalid value",
            "null": "This field cannot be null",
            "blank": "This field cannot be blank",
            "max_length": "Ensure this value has at most 8 characters",
        },
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.title
