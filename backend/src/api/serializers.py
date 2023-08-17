from carts.services import is_shopping_cart_has_recipe
from core.fields import PasswordField
from core.mixins import RequestUserMixin
from core.serializers import LimitListSerializer, PresentableListSerializer
from drf_extra_fields.fields import Base64ImageField
from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag
from recipes.services import (
    get_user_recipes_count,
    recipe_create,
    recipe_update,
)
from rest_framework.serializers import (
    CharField,
    ModelSerializer,
    PrimaryKeyRelatedField,
    Serializer,
    SerializerMethodField,
    StringRelatedField,
)
from users.models import User
from users.services import (
    user_create,
    user_is_subscribed,
    user_recipe_is_favorited,
    user_username_exists,
)

from django.contrib.auth.password_validation import validate_password
from django.utils.translation import gettext as _


class UserSerializer(RequestUserMixin, ModelSerializer):
    is_subscribed = SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
        )

    def get_is_subscribed(self, user):
        return not self.request_user.is_anonymous and user_is_subscribed(
            self.request_user, author=user
        )


class UserCreateSerializer(ModelSerializer):
    password = PasswordField()

    default_error_messages = {
        "already_exists": _("A user with that username already exists.")
    }

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "password",
        )

    def validate_username(self, value):
        if user_username_exists(value):
            self.fail("already_exists")
        return value

    def validate_password(self, value):
        validate_password(value)
        return value

    def create(self, validated_data):
        return user_create(validated_data)


class UserSetPasswordSerializer(RequestUserMixin, Serializer):
    new_password = PasswordField(write_only=False)
    current_password = PasswordField(write_only=False)

    default_error_messages = {"invalid_password": _("Invalid password.")}

    def validate_new_password(self, value):
        validate_password(value)
        return value

    def validate_current_password(self, value):
        if not self.request_user.check_password(value):
            self.fail("invalid_password")
        return value


class UserSubscriptionsRecipeSerializer(ModelSerializer):
    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")
        list_serializer_class = LimitListSerializer


class UserSubscriptionsSerializer(UserSerializer):
    recipes = UserSubscriptionsRecipeSerializer(
        many=True, read_only=True, context={"query_param": "recipes_limit"}
    )
    recipes_count = SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + (
            "recipes",
            "recipes_count",
        )

    def get_recipes_count(self, user):
        return get_user_recipes_count(user)


class UserSubscribeSerializer(UserSubscriptionsSerializer):
    default_error_messages = {
        "not_sub": _("You are not subscribed to {author}."),
        "already_sub": _("You are already subscribed to {author}."),
        "self_subs": _("Subscribing to yourself not allowed."),
    }

    class Meta(UserSubscriptionsSerializer.Meta):
        read_only_fields = UserSubscriptionsSerializer.Meta.fields

    def validate(self, attrs):
        user, author, is_delete = (
            self.initial_data.get("user"),
            self.initial_data.get("author"),
            self.initial_data.get("is_method_delete"),
        )
        is_subscribed = user_is_subscribed(user, author)

        if is_delete and not is_subscribed:
            self.fail("not_sub", author=author)

        if not is_delete and is_subscribed:
            self.fail("already_sub", author=author)

        if user == author:
            self.fail("self_subs", author=author)

        return attrs


class TagSerializer(ModelSerializer):
    class Meta:
        model = Tag
        fields = ("id", "name", "color", "slug")


class IngredientSerializer(ModelSerializer):
    measurement_unit = StringRelatedField()

    class Meta:
        model = Ingredient
        fields = ("id", "name", "measurement_unit")


class RecipeIngredientSerializer(ModelSerializer):
    id = PrimaryKeyRelatedField(
        source="ingredient.id", queryset=Ingredient.objects.all()
    )
    name = CharField(source="ingredient.name", required=False)
    measurement_unit = CharField(
        source="ingredient.measurement_unit", required=False
    )

    class Meta:
        model = RecipeIngredient
        fields = ("id", "name", "measurement_unit", "amount")


class RecipeSerializer(RequestUserMixin, ModelSerializer):
    tags = PresentableListSerializer(
        presentation_serializer=TagSerializer,
        presentation_serializer_kwargs={"many": True},
        child=PrimaryKeyRelatedField(queryset=Tag.objects.all()),
        allow_empty=False,
    )
    ingredients = RecipeIngredientSerializer(many=True, allow_empty=False)
    author = UserSerializer(read_only=True)
    image = Base64ImageField()
    is_favorited = SerializerMethodField()
    is_in_shopping_cart = SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            "id",
            "tags",
            "author",
            "ingredients",
            "is_favorited",
            "is_in_shopping_cart",
            "name",
            "image",
            "text",
            "cooking_time",
        )

    def get_is_favorited(self, recipe):
        return not self.request_user.is_anonymous and user_recipe_is_favorited(
            self.request_user, recipe
        )

    def get_is_in_shopping_cart(self, recipe):
        return (
            not self.request_user.is_anonymous
            and is_shopping_cart_has_recipe(self.request_user, recipe)
        )

    def create(self, valid_data):
        tags, components = (*self._pop_tags_and_components(valid_data),)
        return recipe_create(self.request_user, tags, components, valid_data)

    def update(self, instance, valid_data):
        tags, components = (*self._pop_tags_and_components(valid_data),)
        return recipe_update(instance, tags, components, valid_data)

    def _pop_tags_and_components(self, valid_data):
        tags = valid_data.pop("tags")
        components = {
            item.pop("ingredient").get("id"): item
            for item in valid_data.pop("ingredients")
        }
        return (tags, components)


class RecipeShoppingCartSerializer(UserSubscriptionsRecipeSerializer):
    default_error_messages = {
        "not_in": _("{recipe} is not in the shopping cart."),
        "already_in": _("{recipe} is already in shopping cart."),
    }

    class Meta(UserSubscriptionsRecipeSerializer.Meta):
        read_only_fields = UserSubscriptionsRecipeSerializer.Meta.fields

    def validate(self, attrs):
        user, recipe, is_delete = (
            self.initial_data.get("user"),
            self.initial_data.get("recipe"),
            self.initial_data.get("is_method_delete"),
        )
        is_in_shopping_cart = is_shopping_cart_has_recipe(user, recipe)

        if is_delete and not is_in_shopping_cart:
            self.fail("not_in", recipe=recipe)

        if not is_delete and is_in_shopping_cart:
            self.fail("already_in", recipe=recipe)

        return attrs


class RecipeFavoriteSerializer(UserSubscriptionsRecipeSerializer):
    default_error_messages = {
        "not_in": _("User doesn't have {recipe} in favorites."),
        "already_in": _("{recipe} is already in favorites."),
    }

    class Meta(UserSubscriptionsRecipeSerializer.Meta):
        read_only_fields = UserSubscriptionsRecipeSerializer.Meta.fields

    def validate(self, attrs):
        user, recipe, is_delete = (
            self.initial_data.get("user"),
            self.initial_data.get("recipe"),
            self.initial_data.get("is_method_delete"),
        )
        is_favorite = user_recipe_is_favorited(user, recipe)

        if is_delete and not is_favorite:
            self.fail("not_in", recipe=recipe)

        if not is_delete and is_favorite:
            self.fail("already_in", recipe=recipe)

        return attrs
