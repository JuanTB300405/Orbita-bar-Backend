from rest_framework import serializers
from ..models import Compras, DetallesCompras, Productos
from .detallesComprasSerializer import DetallesComprasSerializer
from .productosSerializer import ProductosSerializer
from django.db import transaction
from datetime import timedelta
from django.utils import timezone
from .notificacionesSerializer import NotificacionesSerializer

class ComprasSerializer(serializers.ModelSerializer):
    detallesCompra = DetallesComprasSerializer(many=True)

    class Meta:
        model = Compras
        fields = ["id", "subtotal", "fecha", "detallesCompra"]

    def create(self, validated_data):
        detalles_data = validated_data.pop('detallesCompra', [])
        if not detalles_data:
            raise serializers.ValidationError({"detallesCompra": "Debe proporcionar al menos un detalle de compra."})

        compra = Compras.objects.create(**validated_data)

        productos_afectados = set()

        for detalle in detalles_data:
            producto = detalle['idproducto']
            cantidad = detalle['cantidad']
            DetallesCompras.objects.create(idcompra=compra, **detalle)

            ProductosSerializer.aumentar_cantidad_inicial_inventario(producto.id, cantidad)
            ProductosSerializer.aumentar_cantidad_inventario(producto.id, cantidad)
            
            productos_afectados.add(producto)

        for producto in productos_afectados:
            NotificacionesSerializer.verificar_tope_minimo(producto)


        return compra

    def _serializar_detalle(self, detalle):
        return {
            'id': detalle.id,
            'idproducto': detalle.idproducto.id,
            'producto_nombre': detalle.idproducto.nombre,  # Asume que existe
            'cantidad': detalle.cantidad
        }


    def update(self, instance, validated_data):
        try:
            with transaction.atomic():  # Todas las operaciones son atómicas
                detalles_data = validated_data.pop('detallesCompra', [])
                # Validación básica de los datos entrantes
                if not detalles_data:
                    raise serializers.ValidationError({"detallesCompra": "Debe proporcionar al menos un detalle de compra."})
                
                # Actualizar campos simples de la compra
                instance.subtotal = validated_data.get('subtotal', instance.subtotal)
                instance.fecha = validated_data.get('fecha', instance.fecha)
                instance.save()

                # Procesar detalles de compra
                self._procesar_detalles_compra(instance, detalles_data)
                
                # Refrescar la instancia para incluir los cambios
                instance.refresh_from_db()

                for detalle in instance.detallesCompra.all():
                    print("detalle", detalle.idproducto)
                    NotificacionesSerializer.verificar_tope_minimo(detalle.idproducto)

                return {
                'status': 'success',
                'code': 200,
                'data': {
                    'id': instance.id,
                    'subtotal': instance.subtotal,
                    'fecha': instance.fecha,
                    'detalles': [self._serializar_detalle(d) for d in instance.detallesCompra.all()]
                }
            }

                
        except Exception as e:
        # Registra el error completo (útil para depuración)
            print(f"Error en update: {str(e)}")#, exc_info=True)
            raise serializers.ValidationError({
                'status': 'error',
                'code': 400,
                'message': str(e),
                'details': getattr(e, 'detail', None)
            })

 
    def _procesar_detalles_compra(self, instance, detalles_data):

        detalles_existentes = {d.id: d for d in instance.detallesCompra.all()}

        for detalle_data in detalles_data:
            detalle_id = detalle_data.get('id')
            if not detalle_id:
                continue  # ignorar sin ID
            
            if detalle_id in detalles_existentes:
                self._actualizar_detalle_existente(detalles_existentes[detalle_id], detalle_data)
            else:
                raise serializers.ValidationError({
                    "id": f"Detalle con ID {detalle_id} no pertenece a esta compra."
                })


    def _actualizar_detalle_existente(self, detalle, detalle_data):
        producto = detalle.idproducto
        producto_nuevo = detalle_data.get('idproducto', producto)
        cantidad_original = detalle.cantidad
        cantidad_nueva = detalle_data.get('cantidad', cantidad_original)

        producto_nuevo_id = producto_nuevo.id if hasattr(producto_nuevo, 'id') else producto_nuevo
        producto_id = producto.id if hasattr(producto, 'id') else producto

        # Para comparar productos correctamente
        diferente_producto = producto_nuevo_id != producto_id

        ahora = timezone.now()
        hace_24h = detalle.created_at + timedelta(hours=24)
        modificar_inventario = (
            ahora <= hace_24h and (
                cantidad_nueva != cantidad_original or diferente_producto
            )
        )

        if modificar_inventario:
        # Primero revertir el inventario del producto original
            ProductosSerializer.reducir_cantidad_inventario(producto_id, cantidad_original)
            ProductosSerializer.reducir_cantidad_inicial_inventario(producto_id, cantidad_original)
            # NotificacionesSerializer.verificar_tope_minimo(producto)

        for attr, value in detalle_data.items():
            setattr(detalle, attr, value)
        detalle.save()

        if modificar_inventario:
            # Luego aumentar inventario del nuevo producto
            ProductosSerializer.aumentar_cantidad_inventario(producto_nuevo_id, cantidad_nueva)
            ProductosSerializer.aumentar_cantidad_inicial_inventario(producto_nuevo_id, cantidad_nueva)
            # NotificacionesSerializer.verificar_tope_minimo(producto_nuevo)

    def _revertir_inventario_si_aplica(self, detalle):
        ahora = timezone.now()
        if ahora <= detalle.created_at + timedelta(hours=24):
            try:
                producto_id = detalle.idproducto.id
                cantidad = detalle.cantidad
                ProductosSerializer.reducir_cantidad_inventario(producto_id, cantidad)
                ProductosSerializer.reducir_cantidad_inicial_inventario(producto_id, cantidad)
                NotificacionesSerializer.verificar_tope_minimo(detalle.idproducto)
            except Exception as e:
                print(f"Advertencia: no se pudo revertir inventario para el detalle {detalle.id}: {e}")

    def delete(self, instance):
        for detalle in instance.detallesCompra.all():
            self._revertir_inventario_si_aplica(detalle)
        instance.delete()
        return {"status": "success", "message": f"Compra {instance.id} eliminada correctamente"}

