from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from django.shortcuts import get_object_or_404

from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    RecipeTag,
    ShoppingCart,
    Tag,
)
from users.models import Subscription, User


class CustomUserCreateSerializer(UserCreateSerializer):
    """User Creation Serializer."""

    class Meta:
        model = User
        fields = ["email", "username", "first_name", "last_name", "password"]


class CustomUserSerializer(UserSerializer):
    """User Model Serializer."""

    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
        ]

    def get_is_subscribed(self, obj):
        request = self.context.get("request")
        if request is None or request.user.is_anonymous:
            return False
        return Subscription.objects.filter(
            user=request.user, author=obj
        ).exists()


class TagSerializer(serializers.ModelSerializer):
    """Model Viewer Serializer Tag."""

    class Meta:
        model = Tag
        fields = ["id", "name", "color", "slug"]


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Serializer of models linking ingredients and recipes."""

    id = serializers.ReadOnlyField(source="ingredient.id")
    name = serializers.ReadOnlyField(source="ingredient.name")
    measurement_unit = serializers.ReadOnlyField(
        source="ingredient.measurement_unit"
    )

    class Meta:
        model = RecipeIngredient
        fields = ["id", "name", "amount", "measurement_unit"]


class IngredientSerializer(serializers.ModelSerializer):
    """The serializer for viewing the Ingredients models."""

    class Meta:
        model = Ingredient
        fields = ["id", "name", "measurement_unit"]


class RecipeSerializer(serializers.ModelSerializer):
    """Model View Serializer Recipe."""

    tags = TagSerializer(many=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField(
        method_name="get_is_favorited"
    )
    is_in_shopping_cart = serializers.SerializerMethodField(
        method_name="get_is_in_shopping_cart"
    )

    class Meta:
        model = Recipe
        fields = [
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
        ]

    def get_ingredients(self, obj):
        ingredients = RecipeIngredient.objects.filter(recipe=obj)
        return RecipeIngredientSerializer(ingredients, many=True).data

    def get_is_favorited(self, obj):
        request = self.context.get("request")
        if request is None or request.user.is_anonymous:
            return False
        return Favorite.objects.filter(
            user=request.user, recipe_id=obj
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get("request")
        if request is None or request.user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(
            user=request.user, recipe_id=obj
        ).exists()


class AddIngredientRecipeSerializer(serializers.ModelSerializer):
    """Serializer for adding ingredients to a recipe."""

    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ["id", "amount"]


class CreateRecipeSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating recipes."""

    author = CustomUserSerializer(read_only=True)
    ingredients = AddIngredientRecipeSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = [
            "id",
            "author",
            "ingredients",
            "tags",
            "image",
            "name",
            "text",
            "cooking_time",
        ]

    def validate(self, data):
        ingredients = self.initial_data.get("ingredients")
        list = []
        for ingredient_one in ingredients:
            amount = ingredient_one["amount"]
            if int(amount) < 1:
                raise serializers.ValidationError(
                    {"amount": "Количество ингредиентов должно быть больше 0!"}
                )
            if ingredient_one["id"] in list:
                raise serializers.ValidationError(
                    {"ingredient": "Ингредиенты должны быть уникальными!"}
                )
            list.append(ingredient_one["id"])
        return data

    def create_ingredients(self, ingredients, recipe):
        for ingredient_one in ingredients:
            ingredient = Ingredient.objects.get_object_or_404(
                id=ingredient_one["id"]
            )
            RecipeIngredient.objects.create(
                ingredient=ingredient,
                recipe=recipe,
                amount=ingredient_one["amount"],
            )

    def create_tags(self, tags, recipe):
        for tag in tags:
            RecipeTag.objects.create(recipe=recipe, tag=tag)

    def create(self, validated_data):
        """
        Creating recipes.
        Available only to authorized users.
        """
        ingredients = validated_data.pop("ingredients")
        tags = validated_data.pop("tags")
        author = self.context.get("request").user
        recipe = Recipe.objects.create(author=author, **validated_data)
        self.create_ingredients(ingredients, recipe)
        self.create_tags(tags, recipe)
        return recipe

    def update(self, instance, validated_data):
        """
        Changing the recipe.
        Available only to authors.
        """
        tags = validated_data.pop("tags")
        ingredients = validated_data.pop("ingredients")
        instance = super().update(instance, validated_data)
        instance.tags.clear()
        instance.tags.set(tags)
        instance.ingredients.clear()
        self.create_ingredients_amounts(
            recipe=instance, ingredients=ingredients
        )
        instance.save()
        return instance

    def to_representation(self, instance):
        return RecipeSerializer(
            instance, context={"request": self.context.get("request")}
        ).data


class ShowFavoriteSerializer(serializers.ModelSerializer):
    """Serializer for displaying favorites."""

    class Meta:
        model = Recipe
        fields = ["id", "name", "image", "cooking_time"]


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Serializer for the shopping list."""

    class Meta:
        model = ShoppingCart
        fields = ["user", "recipe"]

    def to_representation(self, instance):
        return ShowFavoriteSerializer(
            instance.recipe, context={"request": self.context.get("request")}
        ).data


class FavoriteSerializer(serializers.ModelSerializer):
    """Model Serializer Favorites."""

    class Meta:
        model = Favorite
        fields = ["user", "recipe"]

    def to_representation(self, instance):
        return ShowFavoriteSerializer(
            instance.recipe, context={"request": self.context.get("request")}
        ).data


class ShowSubscriptionsSerializer(serializers.ModelSerializer):
    """Serializer for displaying user subscriptions."""

    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "recipes",
            "recipes_count",
        ]

    def get_is_subscribed(self, obj):
        request = self.context.get("request")
        if request is None or request.user.is_anonymous:
            return False
        return Subscription.objects.filter(
            user=request.user, author=obj
        ).exists()

    def get_recipes(self, obj):
        request = self.context.get("request")
        if not request or request.user.is_anonymous:
            return False
        recipes = Recipe.objects.filter(author=obj)
        limit = request.query_params.get("recipes_limit")
        if limit:
            recipes = recipes[: int(limit)]
        return ShowFavoriteSerializer(
            recipes, many=True, context={"request": request}
        ).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class SubscriptionSerializer(serializers.ModelSerializer):
    """Subscription Serializer."""

    class Meta:
        model = Subscription
        fields = ["user", "author"]
        validators = [
            UniqueTogetherValidator(
                queryset=Subscription.objects.all(),
                fields=["user", "author"],
            )
        ]

    def to_representation(self, instance):
        return ShowSubscriptionsSerializer(
            instance.author, context={"request": self.context.get("request")}
        ).data
