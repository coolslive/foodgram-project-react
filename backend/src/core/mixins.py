from rest_framework.response import Response


class ActionSerializerMixin:
    action_serializer = {}

    def get_serializer_class(self):
        return self.action_serializer.get(self.action, self.serializer_class)


class ActionPermissionMixin:
    action_permission = {}

    def get_permissions(self):
        for action, permission_class in self.action_permission.items():
            if self.action == action:
                self.permission_classes = [permission_class]
        return super().get_permissions()


class RequestUserMixin:
    @property
    def request_user(self):
        return self.context.get("request").user


class UserRetrieveModelMixin:
    lookup_user_method = "me"

    def retrieve(self, request, *args, **kwargs):
        if self.action != self.lookup_user_method:
            return Response(self.get_serializer(self.get_object()).data)
        return Response(self.get_serializer(request.user).data)


class ValidateSerializerMixin:
    def validate(self, data):
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        return serializer
