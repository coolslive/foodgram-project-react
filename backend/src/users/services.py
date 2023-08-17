from recipes.models import Recipe

from django.db.models import QuerySet

from .models import Subscription, User


def user_create(data: dict[str, any]) -> User:
    return User.objects.create_user(**data)


def user_set_password(user: User, new_password: str) -> None:
    user.set_password(new_password)
    user.save()


def user_unsubscribe(user: User, author_id: str | int) -> None:
    Subscription.objects.filter(
        user=user, author=User.objects.get(id=author_id)
    ).delete()


def user_subscribe(user: User, author_id: str | int):
    Subscription.objects.create(
        user=user, author=User.objects.get(id=author_id)
    )


def user_recipe_is_favorited(user: User, recipe: Recipe) -> bool:
    return user.favorites.filter(recipe=recipe).exists()


def user_is_subscribed(user: User, author: User) -> bool:
    return user.subscribers.filter(author=author).exists()


def user_subscriptions_filter(
    authors: QuerySet[User], user: User
) -> QuerySet[User]:
    return authors.filter(subscriptions__user=user)


def user_username_exists(username: str) -> bool:
    return User.objects.filter(username__iexact=username).exists()
