from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.status import HTTP_400_BAD_REQUEST
from rest_framework.decorators import action

from core.services import create_shoping_list
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
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
        author = get_object_or_404(User, id=id)
        if Subscription.objects.filter(
            user=request.user.id, author=author.id
        ).delete():
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class ShowSubscriptionsView(ListAPIView):
    """Displaying subscriptions."""

    permission_classes = [
        IsAuthenticated,
    ]
    pagination_class = CustomPagination

    def get(self, request):
        user = request.user
        queryset = User.objects.filter(author__user=user)
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
        recipe = get_object_or_404(Recipe, id=id)
        if Favorite.objects.filter(user=request.user, recipe=recipe).exists():
            Favorite.objects.filter(user=request.user, recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)


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
    queryset = Recipe.objects.all().select_related("author")
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
        recipe = get_object_or_404(Recipe, id=id)
        if ShoppingCart.objects.filter(
            user=request.user.id, recipe=recipe.id
        ).delete():
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(methods=("get",), detail=False)
    def download_shopping_cart(self, request: WSGIRequest) -> Response:
        """Downloads a file with a shopping list."""
        user = self.request.user
        if not user.carts.exists():
            return Response(status=HTTP_400_BAD_REQUEST)

        filename = f"{user.username}_shopping_list.txt"
        shopping_list = create_shoping_list(user)
        response = HttpResponse(
            shopping_list, content_type="text.txt; charset=utf-8"
        )
        response["Content-Disposition"] = f"attachment; filename={filename}"
        return response
# Даное ревью мне нужно для подтверждение моей мысли,
# в печке ответа не дали.
# В виду того что замечание от тебя, прошу дать отмашку
# верно мылю или нет. И могу ли приступить.
# По выносу отдельного метода натолкнула меня на мысль
# переделать проект, и вот почему:
# Считаю что правельнее будет создавать отдельную
# папку ядро, в котором будут обрабатываться
# создание файла и иные сервисные функции.
# Есть мнение использовать миксины.
# и еще несколько сопутствующих переделок.
# Часть правок уже начал вносить.
# Для верности решил у тебя уточнить.
