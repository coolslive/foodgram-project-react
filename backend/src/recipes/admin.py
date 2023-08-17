from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext as _

from .models import Favorite, Ingredient, Recipe, RecipeIngredient, Tag, Unit


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 0


@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "name_plural_first_form",
        "name_plural_second_form",
    )
    list_display_links = ("id", "name")


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "measurement_unit")
    list_display_links = ("id", "name")
    list_filter = ("measurement_unit__name", "name")
    search_fields = ("name",)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "get_color", "slug")
    list_display_links = ("id", "name")
    search_fields = ("name",)

    @admin.action(description=_("color"))
    def get_color(self, tag):
        """Getting color field into the changelist_form as an html widget."""
        html_input_color = (
            '<input type="color" disabled name="color" value="{color}" '
            'required="" id="id_color">'
        )
        return format_html(html_input_color.format(color=tag.color))


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "cooking_time",
        "author",
        "pub_date",
        "favorites_count",
    )
    list_display_links = ("id", "name")
    list_filter = ("tags", "name", "author")
    search_fields = (
        "tags__name",
        "name",
        "author__username",
        "author__first_name",
        "author__last_name",
    )
    inlines = (RecipeIngredientInline,)

    @admin.action(description=_("favorites"))
    def favorites_count(self, recipe):
        return recipe.favorites.count()

    @admin.action(description=_("tags"))
    def tags_name(self, recipe):
        return recipe.tags.all().get().values()


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ("__str__", "user", "recipe")
    search_fields = ("user__username", "recipe__name", "recipe__text")
