import json
import pathlib

from recipes.models import Ingredient, Unit

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils.translation import gettext as _


class Command(BaseCommand):
    help = "Load ingredients from data/ingredients.json file."
    messages = {
        "begin": _("Loading..."),
        "end": _("Loaded {} units, {} " "ingredients!"),
    }

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS(self.messages.get("begin")))
        ingredients_path = pathlib.Path(
            settings.BASE_DIR / "../data/ingredients.json"
        )

        try:
            with open(str(ingredients_path), "r") as file:
                units_count, ingredients_count = self.loader(
                    json.loads(file.read())
                )
        except Exception as exc:
            raise CommandError(exc)

        self.stdout.write(
            self.style.SUCCESS(
                self.messages.get("end").format(units_count, ingredients_count)
            )
        )

    def loader(self, data):
        begin_unit_count = Unit.objects.count()
        begin_ingredients_count = Ingredient.objects.count()

        self.create_units(data)
        self.create_ingredients(data)

        return (
            Unit.objects.count() - begin_unit_count,
            Ingredient.objects.count() - begin_ingredients_count,
        )

    def create_units(self, data):
        batch = [Unit(name=e.get("measurement_unit")) for e in data]
        Unit.objects.bulk_create(ignore_conflicts=True, objs=batch)

    def create_ingredients(self, data):
        units = self.get_units_map()
        batch = [
            Ingredient(
                name=e.get("name"),
                measurement_unit=units.get(e.get("measurement_unit")),
            )
            for e in data
        ]
        Ingredient.objects.bulk_create(ignore_conflicts=True, objs=batch)

    def get_units_map(self):
        return Unit.objects.in_bulk(field_name="name")
