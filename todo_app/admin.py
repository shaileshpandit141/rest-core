from django.contrib import admin

from .models import SubTask, Tag, Todo


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = [
        field.name
        for field in Tag._meta.get_fields()
        if not (field.many_to_many or field.one_to_many)
    ]
    list_display_links = list_display
    ordering = ("-id",)
    list_filter = []
    search_fields = ["title"]


@admin.register(Todo)
class TodoAdmin(admin.ModelAdmin):
    list_display = [
        field.name
        for field in Todo._meta.get_fields()
        if not (field.many_to_many or field.one_to_many)
    ]
    list_display_links = list_display
    ordering = ("-id",)
    list_filter = ["completed_at", "priority", "status", "tags", "is_deleted"]
    search_fields = ["owner", "title", "description"]


@admin.register(SubTask)
class SubTaskAdmin(admin.ModelAdmin):
    list_display = [
        field.name
        for field in SubTask._meta.get_fields()
        if not (field.many_to_many or field.one_to_many)
    ]
    list_display_links = list_display
    ordering = ("-id",)
    list_filter = ["todo", "is_done"]
    search_fields = ["title"]
