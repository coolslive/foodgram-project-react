from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext as _


class User(AbstractUser):
    email = models.EmailField(
        _("email address"),
        unique=True,
        help_text=_("Required. 254 characters or fewer."),
    )
    password = models.CharField(
        _("password"),
        max_length=150,
        help_text=_("Required. 150 characters or fewer."),
    )
    first_name = models.CharField(
        _("first name"),
        max_length=150,
        help_text=_("Required. 150 characters or fewer."),
    )
    last_name = models.CharField(
        _("last name"),
        max_length=150,
        help_text=_("Required. 150 characters or fewer."),
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = (
        "username",
        "first_name",
        "last_name",
    )

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")
        constraints = (
            models.UniqueConstraint(
                models.functions.Upper("username"),
                name="username case-insensitive",
            ),
        )

    def __str__(self):
        return self.username


class Subscription(models.Model):
    date = models.DateTimeField(
        _("Subscribe date"), auto_now=True, auto_created=True
    )

    user = models.ForeignKey(
        "users.User", related_name="subscribers", on_delete=models.CASCADE
    )
    author = models.ForeignKey(
        "users.User", related_name="subscriptions", on_delete=models.CASCADE
    )

    class Meta:
        ordering = ("-id",)
        verbose_name = _("Subscription")
        verbose_name_plural = _("Subscriptions")
        constraints = (
            models.UniqueConstraint(
                fields=("user", "author"), name="unique pair user -> author"
            ),
            models.CheckConstraint(
                check=~models.Q(author=models.F("user")),
                name="self-subscription",
            ),
        )

    def __str__(self):
        return _(f"{self.user} subscribed to {self.author}")
