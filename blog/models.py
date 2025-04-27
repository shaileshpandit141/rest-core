from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone
from django.utils.text import slugify

User = get_user_model()


class BlogPost(models.Model):
    """Model class for BlogPost"""

    class Meta:
        db_table = "blog_post"
        verbose_name = "blog post"
        verbose_name_plural = "blog posts"
        ordering = ["-id"]

    objects = models.Manager()

    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("published", "Published"),
    ]

    title = models.CharField(
        max_length=255,
        unique=True,
        blank=False,
        null=False,
        db_index=True,
        error_messages={
            "required": "Please enter a blog post title.",
            "invalid": "Please enter a valid title.",
            "null": "Title field cannot be null.",
            "blank": "Title field cannot be empty.",
            "max_length": "Title must be at most 255 characters long.",
        },
    )
    slug = models.SlugField(
        max_length=60,
        unique=True,
        blank=True,
        null=True,
        allow_unicode=False,
        db_index=True,
        error_messages={
            "invalid": (
                "Enter a valid slug consisting of letters, numbers, underscores, or hyphens."
            ),
            "max_length": "Slug must be at most 60 characters long.",
        },
    )
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="blog_posts",
        blank=False,
        null=False,
        db_index=True,
        error_messages={
            "invalid": "Select a valid user.",
            "invalid_choice": "The selected owner is not a valid choice.",
            "null": "Owner field cannot be null.",
            "blank": "Owner field cannot be empty.",
            "does_not_exist": "The specified user does not exist.",
        },
    )
    content = models.TextField(
        blank=True,
        null=True,
        default="Describe your blog post here...",
        error_messages={
            "invalid": "Please enter valid content.",
        },
    )
    status = models.CharField(
        max_length=10,
        blank=False,
        null=False,
        default="draft",
        choices=STATUS_CHOICES,
        error_messages={
            "invalid": "Select a valid status.",
            "max_length": "Status must be at most 10 characters long.",
        },
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs) -> None:
        if not self.slug:
            self.slug = slugify(f"{self.title}-{timezone.now().timestamp()}")
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.title
