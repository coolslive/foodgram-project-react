from django.db.models.signals import pre_delete, pre_save
from django.dispatch import receiver

from .models import Recipe


@receiver([pre_delete], sender=Recipe)
def delete_recipe_image(sender, instance, *args, **kwargs):
    instance.image.delete()


@receiver([pre_save], sender=Recipe)
def delete_old_recipe_image(sender, instance, *args, **kwargs):
    try:
        old_instance = sender.objects.get(pk=instance.id)
    except sender.DoesNotExist:
        return None

    if old_instance.image.name == instance.image.name:
        return None

    old_instance.image.delete(save=False)
