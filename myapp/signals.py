# myapp/signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import RiesgoSiniestralidad, LastDataUpdate

@receiver(post_save, sender=RiesgoSiniestralidad)
def update_last_data_on_save(sender, instance, **kwargs):
    """
    Actualiza el timestamp de LastDataUpdate cuando un objeto RiesgoSiniestralidad
    es guardado (creado o modificado).
    """
    # Obtén el único registro de LastDataUpdate o créalo si no existe.
    # El método .get_or_create() es ideal para esto.
    # Dado que auto_now=True está en last_updated, solo necesitamos llamarle a save().
    obj, created = LastDataUpdate.objects.get_or_create(pk=1) # Usamos pk=1 para asegurar que es siempre el mismo objeto
    obj.save()
    print(f"DEBUG: LastDataUpdate actualizado por post_save de RiesgoSiniestralidad. Nuevo timestamp: {obj.last_updated}")


@receiver(post_delete, sender=RiesgoSiniestralidad)
def update_last_data_on_delete(sender, instance, **kwargs):
    """
    Actualiza el timestamp de LastDataUpdate cuando un objeto RiesgoSiniestralidad
    es eliminado.
    """
    # Obtén el único registro de LastDataUpdate o créalo si no existe.
    obj, created = LastDataUpdate.objects.get_or_create(pk=1)
    obj.save()
    print(f"DEBUG: LastDataUpdate actualizado por post_delete de RiesgoSiniestralidad. Nuevo timestamp: {obj.last_updated}")