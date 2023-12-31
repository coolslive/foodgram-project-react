from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import UniqueConstraint

User = get_user_model()


class Ingredient(models.Model):
    """Ingredients Model."""

    name = models.CharField("Название ингредиентов", max_length=200)
    measurement_unit = models.CharField("Единицы измерениий", max_length=200)

    class Meta:
        ordering = ["name"]
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"
        constraints = [
            UniqueConstraint(
                fields=["name", "measurement_unit"],
                name="ingredient_name_unit_unique",
            )
        ]


class Tag(models.Model):
    """Tag Model."""

    name = models.CharField("Название тега", unique=True, max_length=200)
    color = models.CharField("Цвет", unique=True, max_length=7)
    slug = models.SlugField("Slug", unique=True, max_length=200)

    class Meta:
        ordering = ["name"]
        verbose_name = "Тег"
        verbose_name_plural = "Теги"

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Recipe Model."""

    tags = models.ManyToManyField(
        Tag, through="RecipeTag", verbose_name="Теги", related_name="tags"
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="recipes_model",
        verbose_name="Автор рецепта",
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through="RecipeIngredient",
        verbose_name="Ингредиенты",
        related_name="ingredient",
    )
    image = models.ImageField("Изображение", upload_to="recipes/images/")
    name = models.CharField("Название рецепта", max_length=200)
    text = models.TextField(
        "Описание рецепта", help_text="Введите описание рецепта"
    )
    cooking_time = models.PositiveIntegerField(
        verbose_name="Время приготовления",
        validators=[
            MinValueValidator(
                1, message="Время приготовления должно быть не менее 1 минуты!"
            )
        ],
    )
    pub_date = models.DateTimeField(
        "Время публикации",
        auto_now_add=True,
    )

    class Meta:
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"
        ordering = ("-pub_date",)

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    """A model of the relationship between ingredients and recipes."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name="Рецепт",
        related_name="recipe_ingredient_model",
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name="Ингредиент",
        related_name="ingredient_model",
    )
    amount = models.SmallIntegerField(
        verbose_name="Количество", validators=[MinValueValidator(1)]
    )

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=["recipe", "ingredient"],
                name="recipe_ingredient_unique",
            )
        ]


class RecipeTag(models.Model):
    """The model of the tag and recipe relationship."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name="Рецепт",
        related_name="recipe_tag_model",
    )
    tag = models.ForeignKey(
        Tag, on_delete=models.CASCADE, verbose_name="Тег", related_name="tag"
    )

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=["recipe", "tag"], name="recipe_tag_unique"
            )
        ]


class ShoppingCart(models.Model):
    """Basket model."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
        related_name="shopping_cart",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name="Рецепт",
        related_name="shopping_cart",
    )

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=["user", "recipe"], name="user_shoppingcart_unique"
            )
        ]


class Favorite(models.Model):
    """The Favorites model."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
        related_name="favorites",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name="Рецепт",
        related_name="favorites",
    )

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=["user", "recipe"], name="user_favorite_unique"
            )
        ]
