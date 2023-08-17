from carts.services import (
    shopping_cart_add,
    shopping_cart_delete,
    shopping_cart_to_pdf,
)
from core.backends import (
    ActionBasedFilterBackend,
    IngredientSearchFilterBackend,
)
from core.mixins import (
    ActionPermissionMixin,
    ActionSerializerMixin,
    UserRetrieveModelMixin,
    ValidateSerializerMixin,
)
from django_filters.rest_framework import DjangoFilterBackend
from recipes.models import Ingredient, Recipe, Tag
from recipes.services import (
    user_recipe_add_to_favorite,
    user_recipe_delete_from_favorite,
)
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from users.models import User
from users.services import user_set_password, user_subscribe, user_unsubscribe

from django.http.response import HttpResponse
from django.utils.translation import gettext as _

from .filters import RecipeFilter, UserSubscriptionsFilter
from .pagination import PageNumberLimitPagination
from .permissions import IsOwnerOrReadOnly
from .serializers import (
    IngredientSerializer,
    RecipeFavoriteSerializer,
    RecipeSerializer,
    RecipeShoppingCartSerializer,
    TagSerializer,
    UserCreateSerializer,
    UserSerializer,
    UserSetPasswordSerializer,
    UserSubscribeSerializer,
    UserSubscriptionsRecipeSerializer,
    UserSubscriptionsSerializer,
)


class UsersViewSet(
    ValidateSerializerMixin,
    ActionSerializerMixin,
    ActionPermissionMixin,
    UserRetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    queryset = User.objects.all()
    http_method_names = ["get", "post", "delete"]
    pagination_class = PageNumberLimitPagination
    filter_backends = (ActionBasedFilterBackend,)
    action_filterset_class = {
        "subscriptions": UserSubscriptionsFilter,
    }
    serializer_class = UserSerializer
    action_serializer = {
        "create": UserCreateSerializer,
        "set_password": UserSetPasswordSerializer,
        "subscriptions": UserSubscriptionsSerializer,
        "subscribe": UserSubscribeSerializer,
        "unsubscribe": UserSubscribeSerializer,
    }
    action_permission = {
        "list": AllowAny,
        "create": AllowAny,
        "retrieve": AllowAny,
    }

    @action(["get"], False, name=_("Me"))
    def me(self, request):
        return self.retrieve(request)

    @action(["post"], False, name=_("Set password"))
    def set_password(self, request):
        new_password = self.validate(request.data).data.get("new_password")
        user_set_password(request.user, new_password)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(["get"], False, name=_("Subscriptions"))
    def subscriptions(self, request):
        return self.list(request)

    @action(["post"], True, name=_("Subscribe"))
    def subscribe(self, request, pk=None):
        self.validate_action()
        user_subscribe(request.user, pk)
        return self.retrieve(request)

    @subscribe.mapping.delete
    def unsubscribe(self, request, pk=None):
        self.validate_action()
        user_unsubscribe(request.user, pk)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def validate_action(self):
        self.validate(
            {
                "user": self.request.user,
                "author": self.get_object(),
                "is_method_delete": self.request.method == "DELETE",
            }
        )


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [AllowAny]


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [AllowAny]
    filter_backends = (IngredientSearchFilterBackend,)
    search_fields = ("name",)


class RecipeViewSet(
    ValidateSerializerMixin,
    ActionSerializerMixin,
    ActionPermissionMixin,
    viewsets.ModelViewSet,
):
    http_method_names = ["get", "post", "patch", "delete"]
    queryset = Recipe.objects.all()
    pagination_class = PageNumberLimitPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    serializer_class = RecipeSerializer
    action_serializer = {
        "shopping_cart": RecipeShoppingCartSerializer,
        "delete_shopping_cart": RecipeShoppingCartSerializer,
        "favorite": RecipeFavoriteSerializer,
        "delete_favorite": RecipeFavoriteSerializer,
        "download_shopping_cart": UserSubscriptionsRecipeSerializer,
    }
    action_permission = {
        "list": AllowAny,
        "retrieve": AllowAny,
        "partial_update": IsOwnerOrReadOnly,
        "destroy": IsOwnerOrReadOnly,
    }

    @action(["get"], False)
    def download_shopping_cart(self, request):
        return HttpResponse(
            shopping_cart_to_pdf(request.user),
            content_type="application/pdf",
            headers={
                "Content-Disposition": (
                    'attachment; filename="shopping-cart.pdf"'
                )
            },
        )

    @action(["post"], True)
    def shopping_cart(self, request, pk=None):
        self.validate_action()
        shopping_cart_add(request.user, pk)
        return self.retrieve(request)

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk=None):
        self.validate_action()
        shopping_cart_delete(request.user, pk)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(["post"], True)
    def favorite(self, request, pk=None):
        self.validate_action()
        user_recipe_add_to_favorite(request.user, pk)
        return self.retrieve(request)

    @favorite.mapping.delete
    def delete_favorite(self, request, pk=None):
        self.validate_action()
        user_recipe_delete_from_favorite(request.user, pk)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def validate_action(self):
        self.validate(
            {
                "user": self.request.user,
                "recipe": self.get_object(),
                "is_method_delete": self.request.method == "DELETE",
            }
        )
