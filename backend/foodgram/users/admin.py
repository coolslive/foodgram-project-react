from typing import Any

from django.conf import settings
from django.contrib import admin
from django.db.models.query import QuerySet
from django.http.request import HttpRequest

from .models import Subscription, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ["username", "email", "first_name", "last_name"]
    list_display_links = ["username"]
    search_fields = ["username", "email"]
    ordering = ["username"]
    empty_value_display = settings.EMPTY


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ["user", "author"]
    list_display_links = ["user"]
    search_fields = [
        "author__username",
        "author__email",
        "user__username",
        "user__email",
    ]
    list_filter = ["author__username", "user__username"]
    empty_value_display = settings.EMPTY

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        return super().get_queryset(request).select_related("author", "user")
