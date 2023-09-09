import io

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from django.db.models import Count, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag,
)
from users.models import Subscription, User

from .filters import IngredientFilter, RecipeFilter
from .pagination import CustomPagination
from .permissions import IsAuthorOrAdminOrReadOnly
from .serializers import (
    CreateRecipeSerializer,
    FavoriteSerializer,
    IngredientSerializer,
    RecipeSerializer,
    ShoppingCartSerializer,
    ShowSubscriptionsSerializer,
    SubscriptionSerializer,
    TagSerializer,
)


class SubscribeView(APIView):
    """Subscriptions/unsubscriptions."""

    permission_classes = [
        IsAuthenticated,
    ]

    def post(self, request, id):
        data = {"user": request.user.id, "author": id}
        serializer = SubscriptionSerializer(
            data=data, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        if Subscription.objects.filter(
            user=request.user.id, author=id
        ).delete()[0] == 0:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ShowSubscriptionsView(ListAPIView):
    """Displaying subscriptions."""

    permission_classes = [
        IsAuthenticated,
    ]
    pagination_class = CustomPagination

    def get(self, request):
        user = request.user
        queryset = User.objects.filter(author__user=user).annotate(
            recipes_count=Count("recipes_model")
        )
        page = self.paginate_queryset(queryset)
        serializer = ShowSubscriptionsSerializer(
            page, many=True, context={"request": request}
        )
        return self.get_paginated_response(serializer.data)


class FavoriteView(APIView):
    """Adding/removing a recipe from favorites."""

    permission_classes = [
        IsAuthenticated,
    ]
    pagination_class = CustomPagination

    def post(self, request, id):
        data = {"user": request.user.id, "recipe": id}
        if not Favorite.objects.filter(
            user=request.user, recipe__id=id
        ).exists():
            serializer = FavoriteSerializer(
                data=data, context={"request": request}
            )
            if serializer.is_valid():
                serializer.save()
                return Response(
                    serializer.data, status=status.HTTP_201_CREATED
                )
        return Response(status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        if Favorite.objects.filter(
            user=request.user.id, recipe=id
        ).delete()[0] == 0:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_204_NO_CONTENT)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Displaying tags."""

    permission_classes = [
        AllowAny,
    ]
    pagination_class = None
    serializer_class = TagSerializer
    queryset = Tag.objects.all()


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Displaying ingredients."""

    permission_classes = [
        AllowAny,
    ]
    pagination_class = None
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    filter_backends = [
        IngredientFilter,
    ]
    search_fields = [
        "^name",
    ]


class RecipeViewSet(viewsets.ModelViewSet):
    """Operations with recipes: add/change/delete/view."""

    permission_classes = [
        IsAuthorOrAdminOrReadOnly,
    ]
    pagination_class = CustomPagination
    queryset = (
        Recipe.objects.all()
        .select_related("author")
        .prefetch_related("ingredients", "tags")
    )
    filter_backends = [
        DjangoFilterBackend,
    ]
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method == "GET":
            return RecipeSerializer
        return CreateRecipeSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context


class ShoppingCartView(APIView):
    """Adding/removing a recipe to the shopping cart."""

    permission_classes = [
        IsAuthenticated,
    ]

    def post(self, request, id):
        data = {"user": request.user.id, "recipe": id}
        recipe = get_object_or_404(Recipe, id=id)
        if not ShoppingCart.objects.filter(
            user=request.user, recipe=recipe
        ).exists():
            serializer = ShoppingCartSerializer(
                data=data, context={"request": request}
            )
            if serializer.is_valid():
                serializer.save()
                return Response(
                    serializer.data, status=status.HTTP_201_CREATED
                )
        return Response(status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        if ShoppingCart.objects.filter(
            user=request.user, recipe=id
        ).delete()[0] == 0:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_204_NO_CONTENT)


class DownloadShopingCartView(APIView):
    permission_classes = [IsAuthenticated]
    http_method_names = ["get"]
    pagination_class = None

    def get(self, request):
        ingredients = (
            RecipeIngredient.objects.filter(
                recipe__shopping_cart__user=request.user
            )
            .values("ingredient__name", "ingredient__measurement_unit")
            .annotate(amount=Sum("amount"))
        )
        ingredient_list = self.write_to_buffer(ingredients=ingredients)
        response = HttpResponse(ingredient_list, content_type="StringIO/plain")
        return response

    def write_to_buffer(self, ingredients):
        ingredient_list = io.StringIO()
        for ingredient in ingredients:
            ingredient_list.write(
                "{name}({measurement_unit}) - {amount}\n".format(
                    name=ingredient.get("ingredient__name"),
                    measurement_unit=ingredient.get(
                        "ingredient__measurement_unit"
                    ),
                    amount=ingredient.get("amount"),
                )
            )
        return ingredient_list.getvalue()
