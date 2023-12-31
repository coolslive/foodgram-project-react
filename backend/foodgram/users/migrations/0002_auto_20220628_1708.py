# Generated by Django 3.2.13 on 2022-06-28 17:08

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models

import users.validators


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="user",
            options={"ordering": ["-pk"]},
        ),
        migrations.AlterField(
            model_name="subscription",
            name="author",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="author",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Автор",
            ),
        ),
        migrations.AlterField(
            model_name="user",
            name="email",
            field=models.EmailField(
                max_length=254, unique=True, verbose_name="Почта"
            ),
        ),
        migrations.AlterField(
            model_name="user",
            name="first_name",
            field=models.CharField(max_length=150, verbose_name="Имя"),
        ),
        migrations.AlterField(
            model_name="user",
            name="last_name",
            field=models.CharField(max_length=150, verbose_name="Фамилия"),
        ),
        migrations.AlterField(
            model_name="user",
            name="username",
            field=models.CharField(
                max_length=150,
                validators=[users.validators.validate_username],
                verbose_name="Юзернейм",
            ),
        ),
    ]
