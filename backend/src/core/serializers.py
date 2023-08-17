from drf_extra_fields.relations import PresentableRelatedFieldMixin
from rest_framework.serializers import (
    IntegerField,
    ListSerializer,
    ValidationError,
)

from django.db.models import Manager


class PresentableListSerializer(PresentableRelatedFieldMixin, ListSerializer):
    pass


class LimitListSerializer(ListSerializer):
    default_query_name = "list_limit"

    def __init__(self, *args, **kwargs):
        context = kwargs.pop("context", {})
        min_value = context.get("min_value", 1)
        allow_null = not context.get("required", False)

        self.query_param = context.get("query_param", self.default_query_name)
        self.query_param_type = IntegerField(
            min_value=min_value, allow_null=allow_null
        )

        super().__init__(*args, **kwargs)

    def to_representation(self, data):
        param_value = self.validate_query_param()

        queryset = data.all() if isinstance(data, Manager) else data
        queryset = queryset[:param_value] if param_value else queryset

        return [self.child.to_representation(data) for data in queryset]

    def validate_query_param(self):
        try:
            query_param_value = self.get_param_value()
            return self.query_param_type.run_validation(query_param_value)
        except ValidationError as exc:
            raise ValidationError({self.query_param: exc.detail})

    def get_param_value(self):
        query_params = self.context.get("request").query_params
        return query_params.get(self.query_param, None)
