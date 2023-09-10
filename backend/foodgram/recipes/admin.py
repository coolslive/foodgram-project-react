from typing import Any

from django.contrib import admin
from django.db.models.query import QuerySet
from django.http.request import HttpRequest

from foodgram.settings import EMPTY

from .models import Favorite, Ingredient, Recipe, ShoppingCart, Tag


class IngredientsInLine(admin.TabularInline):
    model = Recipe.ingredients.through


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "recipe"]
    list_display_links = ["id", "user", "recipe"]
    search_fields = ["user__username", "user__email"]
    empty_value_display = EMPTY

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        return super().get_queryset(request).select_related("user", "recipe")


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "measurement_unit"]
    list_display_links = ["id", "name", "measurement_unit"]
    search_fields = ["name"]
    empty_value_display = EMPTY


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "author", "favorites"]
    list_display_links = ["id", "name", "author", "favorites"]
    search_fields = ["name", "author__username"]
    list_filter = ["author", "tags"]
    empty_value_display = EMPTY
    inlines = (IngredientsInLine,)

    def favorites(self, obj):
        return Favorite.objects.filter(recipe=obj).count()

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        return (
            super()
            .get_queryset(request)
            .select_related("author")
            .prefetch_related("tags", "ingredients")
        )


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "recipe"]
    list_display_links = ["id", "user", "recipe"]
    search_fields = ["user__username", "user__email"]
    empty_value_display = EMPTY

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        return super().get_queryset(request).select_related("user", "recipe")


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "color", "slug"]
    list_display_links = ["id", "name", "color", "slug"]
    search_fields = ["name", "slug"]
    empty_value_display = EMPTY
