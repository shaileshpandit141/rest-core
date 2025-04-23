from django.contrib import admin

from .models import BlogPost


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = [
        field.name
        for field in BlogPost._meta.get_fields()
        if not (field.many_to_many or field.one_to_many)
    ]
    list_display_links = list_display
    ordering = ("-id",)
    list_filter = ["status"]
    search_fields = ["title"]
