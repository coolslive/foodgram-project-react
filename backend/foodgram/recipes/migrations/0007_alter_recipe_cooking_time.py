# Generated by Django 3.2.13 on 2022-06-29 12:51

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("recipes", "0006_auto_20220629_1228"),
    ]

    operations = [
        migrations.AlterField(
            model_name="recipe",
            name="cooking_time",
            field=models.PositiveIntegerField(
                validators=[
                    django.core.validators.MinValueValidator(
                        1,
                        message="Время приготовления должно быть не менее 1 минуты!",
                    )
                ],
                verbose_name="Время приготовления",
            ),
        ),
    ]
