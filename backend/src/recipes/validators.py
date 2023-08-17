from django.core.validators import RegexValidator
from django.utils.regex_helper import _lazy_re_compile
from django.utils.translation import gettext_lazy as _

hex_color_validator = RegexValidator(
    _lazy_re_compile(r"^#[A-Fa-f0-9]{6}$"),
    message=_("Enter a valid hex color, eg. #000000."),
    code="invalid",
)

recipe_title_validator = RegexValidator(
    _lazy_re_compile(r"(?!^[\d()_])^[\w() ]+$"),
    message=_(
        'Enter a valid recipe title, eg. "Tea (black) with lime".\n'
        "The title cannot start with numbers, parentheses, be numbers only "
        "or contains another non-alphabetic symbols."
    ),
    code="invalid",
)
