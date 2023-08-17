from django_filters import rest_framework as filters
from recipes.models import Recipe, Tag
from recipes.services import (
    recipes_in_user_favorites,
    recipes_in_user_shopping_cart,
)
from users.services import user_subscriptions_filter

from django.utils.translation import gettext as _


class RecipeFilter(filters.FilterSet):
    is_favorited = filters.BooleanFilter(
        method="filter_is_favorited", label=_("favorited")
    )
    is_in_shopping_cart = filters.BooleanFilter(
        method="filter_is_in_shopping_cart", label=_("in shopping cart")
    )
    tags = filters.ModelMultipleChoiceFilter(
        field_name="tags__slug",
        to_field_name="slug",
        queryset=Tag.objects.all(),
    )

    class Meta:
        model = Recipe
        fields = (
            "is_favorited",
            "is_in_shopping_cart",
            "author",
            "tags",
        )

    def filter_is_favorited(self, recipes, name, value):
        if self._is_can_filter(value):
            return recipes_in_user_favorites(recipes, self.request.user)
        return recipes

    def filter_is_in_shopping_cart(self, recipes, name, value):
        if self._is_can_filter(value):
            return recipes_in_user_shopping_cart(recipes, self.request.user)
        return recipes

    def _is_can_filter(self, value):
        return value and self.request.user.is_authenticated


class UserSubscriptionsFilter(filters.FilterSet):
    @property
    def qs(self):
        return user_subscriptions_filter(super().qs, self.request.user)
