from django.db import models
from django.utils.translation import gettext_lazy as _


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        "users.User", on_delete=models.CASCADE, verbose_name=_("user")
    )
    recipe = models.ForeignKey(
        "recipes.Recipe", on_delete=models.CASCADE, verbose_name=_("recipe")
    )

    class Meta:
        verbose_name = _("Shopping cart")
        verbose_name_plural = _("Shopping carts")
        default_related_name = "shopping_cart"

    def __str__(self):
        return f"{self.recipe} {self.user}"
