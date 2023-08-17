from core.constants import COOKING_TIME_MIN_VALUE, INGREDIENT_AMOUNT_MIN_VALUE

from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from .fields import RGBColorField
from .validators import recipe_title_validator


class Recipe(models.Model):
    name = models.CharField(
        _("recipe"), max_length=200, validators=[recipe_title_validator]
    )
    text = models.TextField(_("description"))
    cooking_time = models.PositiveSmallIntegerField(
        _("cooking time"),
        default=COOKING_TIME_MIN_VALUE,
        validators=[MinValueValidator(COOKING_TIME_MIN_VALUE)],
    )
    image = models.ImageField(_("image"), upload_to="recipes/images/")
    pub_date = models.DateTimeField(
        _("publication date"), auto_now_add=True, editable=False
    )

    author = models.ForeignKey(
        "users.User",
        related_name="recipes",
        on_delete=models.DO_NOTHING,
        verbose_name=_("author"),
    )
    components = models.ManyToManyField(
        "Ingredient",
        through="RecipeIngredient",
    )
    tags = models.ManyToManyField("Tag")

    class Meta:
        verbose_name = _("Recipe")
        verbose_name_plural = _("Recipes")
        ordering = ("-pub_date",)

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    amount = models.PositiveSmallIntegerField(
        _("amount"),
        default=INGREDIENT_AMOUNT_MIN_VALUE,
        validators=[MinValueValidator(INGREDIENT_AMOUNT_MIN_VALUE)],
    )

    recipe = models.ForeignKey(
        Recipe, related_name="ingredients", on_delete=models.CASCADE
    )
    ingredient = models.ForeignKey(
        "Ingredient", related_name="recipes", on_delete=models.CASCADE
    )

    def __str__(self):
        return f"{self.ingredient} x {self.amount}"


class Unit(models.Model):
    name = models.CharField(_("unit"), max_length=200, unique=True)
    name_plural_first_form = models.CharField(
        _("fist form"),
        max_length=200,
        blank=True,
        null=True,
        help_text="Мне нужно две (единица измерения).",
    )
    name_plural_second_form = models.CharField(
        _("second form"),
        max_length=200,
        blank=True,
        null=True,
        help_text="Мне нужно пять (единица измерения).",
    )

    class Meta:
        verbose_name = _("Measurement unit")
        verbose_name_plural = _("Measurement units")

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(_("tag"), max_length=200)
    color = RGBColorField(_("color"))
    slug = models.SlugField(_("slug"), max_length=200)

    class Meta:
        verbose_name = _("Tag")
        verbose_name_plural = _("Tags")

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(_("ingredient"), max_length=200)

    measurement_unit = models.ForeignKey("Unit", on_delete=models.DO_NOTHING)

    class Meta:
        verbose_name = _("Ingredient")
        verbose_name_plural = _("Ingredients")
        constraints = (
            models.UniqueConstraint(
                fields=("name", "measurement_unit"),
                name="unique pair name -> unit",
            ),
        )

    def __str__(self):
        return self.name


class Favorite(models.Model):
    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)

    class Meta:
        verbose_name = _("Favorite recipe")
        verbose_name_plural = _("Favorite recipes")
        default_related_name = "favorites"
        constraints = (
            models.UniqueConstraint(
                fields=("user", "recipe"), name="unique pair user -> recipe"
            ),
        )

    def __str__(self):
        return _("{recipe} is {user}'s favorite recipe").format(
            recipe=self.recipe, user=self.user
        )
