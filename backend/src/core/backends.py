from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter


class ActionBasedFilterBackend(DjangoFilterBackend):
    def get_filterset_class(self, view, queryset=None):
        action_filterset_class = getattr(view, "action_filterset_class", None)
        if action_filterset_class:
            return action_filterset_class.get(
                view.action, super().get_filterset_class(view, queryset)
            )
        return super().get_filterset_class(view, queryset)


class IngredientSearchFilterBackend(SearchFilter):
    search_param = "name"
    search_regex_templates = ["\A{term}", "(?!\A)\y{term}", "\Y{term}"]
    search_value_min_len = 3
    search_terms_delimiter = ".+"

    def filter_queryset(self, request, queryset, view):
        search_field = self.get_search_fields(view, request)
        search_value = self.get_search_value(request)

        if not search_field or not search_value:
            return queryset

        if len(search_value) < self.search_value_min_len:
            return queryset.none()

        filters = self.construct_search(search_field, search_value)
        querysets = [queryset.filter(**filter) for filter in filters]

        return queryset.none().union(*querysets, all=True)

    def construct_search(self, field_name, search_value):
        filters = [
            {f"{field_name}__iregex": regex_template.format(term=search_value)}
            for regex_template in self.search_regex_templates
        ]
        return filters

    def get_search_fields(self, view, request):
        search_fields = super().get_search_fields(view, request)
        return search_fields[0] if search_fields else ""

    def get_search_value(self, request):
        search_terms = super().get_search_terms(request)
        return self.search_terms_delimiter.join(search_terms)
