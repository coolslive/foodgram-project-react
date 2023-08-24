from enum import Enum, IntEnum


class Tuples(tuple, Enum):
    RECIPE_IMAGE_SIZE = 600, 600
    SYMBOL_TRUE_SEARCH = "1", "true"
    SYMBOL_FALSE_SEARCH = "0", "false"


class Limits(IntEnum):
    MAX_LEN_EMAIL_FIELD = 256
    MAX_LEN_USERS_CHARFIELD = 30
    MIN_LEN_USERNAME = 2
    MAX_LEN_RECIPES_CHARFIELD = 64
    MAX_LEN_MEASUREMENT = 256
    MAX_LEN_RECIPES_TEXTFIELD = 4000
    MIN_COOKING_TIME = 1
    MAX_COOKING_TIME = 400
    MIN_AMOUNT_INGREDIENTS = 1
    MAX_AMOUNT_INGREDIENTS = 32


class UrlQueries(str, Enum):
    SEARCH_ING_NAME = "name"
    FAVORITE = "is_favorited"
    SHOP_CART = "is_in_shopping_cart"
    AUTHOR = "author"
    TAGS = "tags"
