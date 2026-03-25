# sabores/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from ..models import Productos, Notificaciones

@receiver(post_save, sender=Productos)
def verificar_tope_minimo(sender, instance, **kwargs):
    print("ENTRA AL SIGNALS")
    if instance.cantidad_actual <= instance.topeMin:
        notificacion_existente = Notificaciones.objects.filter(
            productoId=instance,
            leida=False
        ).exists()

        if not notificacion_existente:
            Notificaciones.objects.create(
                productoId=instance,
                mensaje=f"El producto '{instance.nombre}' ha alcanzado su tope mínimo ({instance.cantidad_actual})"
            )
    else:
        Notificaciones.objects.filter(
            productoId=instance,
            leida=False
        ).update(leida=True)
