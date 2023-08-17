from django import forms
from django.db import models

from .validators import hex_color_validator


class RGBColorField(models.CharField):
    default_validators = []

    def __init__(self, *args, **kwargs):
        self.default_validators = [hex_color_validator]
        kwargs.setdefault("max_length", 7)
        super().__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        defaults = {
            "form_class": forms.CharField,
            "widget": forms.TextInput(attrs={"type": "color"}),
        }
        kwargs.update(defaults)
        return super().formfield(**defaults)
