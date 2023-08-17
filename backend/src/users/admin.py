from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Subscription, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_filter = (
        "username",
        "email",
        "is_staff",
        "is_superuser",
        "is_active",
        "groups",
    )


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        "__str__",
        "user",
        "author",
        "date",
    )
    list_filter = (
        "user",
        "author",
        "date",
    )
    search_fields = ("user__username", "author__username")
