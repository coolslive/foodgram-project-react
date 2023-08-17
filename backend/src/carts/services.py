from typing import Any

import pdfkit
from recipes.models import Recipe, RecipeIngredient, Unit
from users.models import User

from django.db.models import F, QuerySet, Sum
from django.template.loader import get_template

from .models import ShoppingCart


def shopping_cart_to_pdf(user: User) -> bytes:
    ingredients = shopping_cart_ingredients(user)
    shopping_cart_html = render_html_template(
        "shopping_cart.html", context={"ingredients": ingredients}
    )
    return html_to_pdf(shopping_cart_html)


def shopping_cart_ingredients(user: User) -> QuerySet[dict[str, Any]]:
    return (
        RecipeIngredient.objects.filter(
            recipe__in=user.shopping_cart.values("recipe")
        )
        .order_by("ingredient__name")
        .values(
            name=F("ingredient__name"),
            unit=F("ingredient__measurement_unit__name"),
        )
        .annotate(amount=Sum("amount"))
    )


def render_html_template(template_name: str, context: dict[str, Any]) -> str:
    return get_template(template_name).render(context=context)


def html_to_pdf(html_as_string: str):
    return pdfkit.from_string(html_as_string)


def shopping_cart_add(user: User, recipe_id: str | int) -> None:
    ShoppingCart.objects.update_or_create(
        user=user, recipe=Recipe.objects.get(id=recipe_id)
    )


def shopping_cart_delete(user: User, recipe_id: str | int) -> None:
    ShoppingCart.objects.filter(
        user=user, recipe=Recipe.objects.get(id=recipe_id)
    ).delete()


def is_shopping_cart_has_recipe(user: User, recipe: Recipe) -> bool:
    return user.shopping_cart.filter(recipe=recipe).exists()


def get_unit_plural_forms(unit_name: str) -> dict[str, str]:
    return (
        Unit.objects.filter(name=unit_name)
        .values(
            first=F("name_plural_first_form"),
            second=F("name_plural_second_form"),
        )
        .get()
    )
