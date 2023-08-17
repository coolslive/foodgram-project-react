from recipes.models import Favorite, Ingredient, Recipe, RecipeIngredient, Tag
from users.models import User

from django.db import transaction
from django.db.models import QuerySet


def get_user_recipes_count(user: User) -> int:
    return user.recipes.count()


@transaction.atomic
def recipe_create(
    user: User,
    tags: list[Tag],
    components: dict[Ingredient, dict[str, any]],
    data: dict[str, any],
) -> Recipe:
    obj = Recipe.objects.create(author=user, **data)
    recipe_replace_tags(obj, tags)
    recipe_replace_components(obj, components)
    return obj


@transaction.atomic
def recipe_update(
    instance: Recipe,
    tags: list[Tag],
    components: dict[Ingredient, dict[str, any]],
    data: dict[str, any],
) -> Recipe:
    recipe_update_fields(instance, data)
    recipe_replace_tags(instance, tags)
    recipe_replace_components(instance, components, clear=True)
    return instance


def recipe_replace_tags(instance: Recipe, tags: list[Tag]) -> None:
    instance.tags.set(tags)


def recipe_replace_components(instance, components, clear=False):
    if clear:
        instance.components.clear()
    batch = [
        RecipeIngredient(recipe=instance, ingredient=ingredient, **amount)
        for ingredient, amount in components.items()
    ]
    RecipeIngredient.objects.bulk_create(batch)


def recipe_update_fields(instance: Recipe, data: dict[str, any]) -> None:
    for attr, value in data.items():
        setattr(instance, attr, value)
    instance.save()


def recipes_in_user_favorites(
    recipes: QuerySet[Recipe], user: User
) -> QuerySet[Recipe]:
    return recipes.filter(pk__in=user.favorites.values("recipe"))


def recipes_in_user_shopping_cart(
    recipes: QuerySet[Recipe], user: User
) -> QuerySet[Recipe]:
    return recipes.filter(pk__in=user.shopping_cart.values("recipe"))


def user_recipe_add_to_favorite(user: User, recipe_id: str | int) -> None:
    Favorite.objects.update_or_create(
        user=user, recipe=Recipe.objects.get(id=recipe_id)
    )


def user_recipe_delete_from_favorite(user: User, recipe_id: str | int) -> None:
    Favorite.objects.filter(
        user=user, recipe=Recipe.objects.get(id=recipe_id)
    ).delete()
