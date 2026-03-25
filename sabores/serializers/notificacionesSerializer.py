from rest_framework import serializers
from ..models import Notificaciones
from ..models import Productos
from .productosSerializer import ProductosSerializer
# from django.db.models.signals import post_save
# from django.dispatch import receiver

class NotificacionesSerializer(serializers.ModelSerializer):

    productoId = serializers.PrimaryKeyRelatedField(
        queryset=Productos.objects.all(), write_only=True) 
    producto = ProductosSerializer(source='productoId', read_only=True)
    class Meta:
        model = Notificaciones
        fields = ['id', 'productoId', 'producto', 'fecha', 'leida']

        # sabores/signals.py


    # @receiver(post_save, sender=Productos)
    @staticmethod
    def verificar_tope_minimo(producto):
        print("producto", producto)
        try:
            if producto.cantidad_actual <= producto.topeMin:
                print("entra x2")
                notificacion, creada = Notificaciones.objects.get_or_create(
                    productoId=producto,
                    leida=False
                )

                if creada:
                    estado = "created"
                else:
                    estado = "already_exists"

            else:
                # Si ya superó el tope, marcar como leída (no eliminar)
                updated = Notificaciones.objects.filter(
                    productoId=producto,
                    leida=False
                ).update(leida=True)
                print("update", updated)
                estado = "marked_as_read" if updated else "no_action"

            # Respuesta con datos del producto
            return {
                "status": estado,
                "producto": 
                
                {
                    "id": producto.id,
                    "nombre": producto.nombre,
                    "cantidad_actual": producto.cantidad_actual,
                    "topeMin": producto.topeMin
                }
            }

        except Exception as e:
            print(f"Error en verificar_tope_minimo: {e}")
            return {"status": "error", "message": str(e)}
