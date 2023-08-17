from django.contrib import admin

from .models import ShoppingCart


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ("user", "recipe")
    search_fields = (
        "user__username",
        "user__first_name",
        "user__last_name",
        "recipe__name",
        "recipe__text",
    )
