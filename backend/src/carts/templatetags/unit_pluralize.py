from carts.services import get_unit_plural_forms
from core.constants import (
    PLURAL_FIST_FORM,
    PLURAL_SECOND_FORM,
    PLURAL_WITHOUT_COUNT,
)

from django import template

register = template.Library()


@register.filter
def unit_pluralize(value, count):
    res = "{count} {unit}"

    if value in PLURAL_WITHOUT_COUNT:
        return value

    if count <= PLURAL_FIST_FORM:
        return res.format(count=count, unit=value)

    plural_forms = get_unit_plural_forms(value)

    if count < PLURAL_SECOND_FORM:
        return res.format(count=count, unit=plural_forms.get("first"))

    return res.format(count=count, unit=plural_forms.get("second"))
