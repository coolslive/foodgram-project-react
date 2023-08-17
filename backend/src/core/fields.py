from rest_framework import serializers


class PasswordField(serializers.CharField):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.style = {"input_type": "password"}
