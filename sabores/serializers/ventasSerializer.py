from rest_framework import serializers
from ..models import Ventas, DetallesVentas, Notificaciones,Mesa
from .productosSerializer import ProductosSerializer
from .detallesVentasSerializer import DetallesVentasSerializer
from .notificacionesSerializer import NotificacionesSerializer
from .mesaSerializer import MesaSerializer

class VentasSerializer(serializers.ModelSerializer):

    detallesVentas = DetallesVentasSerializer(many=True)
    mesaId = serializers.PrimaryKeyRelatedField(queryset=Mesa.objects.all(), allow_null=True, required=False)
    mesa = MesaSerializer(source='mesaId', read_only=True)


    class Meta:
        model = Ventas
        fields = ["id", "fecha", "total", "devuelta","mesaId", "mesa", "detallesVentas"]


    def create(self, validated_data):
        detalles_data = validated_data.pop('detallesVentas')
        devuelta = validated_data.pop('devuelta', 0)

        total = 0

        for detalle in detalles_data:
            producto = detalle["idproducto"]
            cantidad = detalle['cantidad']

            if cantidad > producto.cantidad_actual:
                raise ValueError(f"Stock insuficiente para el producto ({producto.nombre})")

            total = total + (producto.precio * cantidad)

        ventas = Ventas.objects.create(**validated_data, total=total, devuelta=devuelta)

        for detalle in detalles_data:
            DetallesVentas.objects.create(idventa=ventas, **detalle)
            producto = detalle['idproducto']
            cantidad = detalle['cantidad']

            ProductosSerializer.reducir_cantidad_inventario(producto.id, cantidad)
            NotificacionesSerializer.verificar_tope_minimo(producto)
            # if producto.cantidad_actual <= producto.topeMin:
            #     Notificaciones.objects.create(
            #         productoId=producto,
            #         mensaje=f"El producto '{producto.nombre}' ha alcanzado su tope mínimo, la cantidad actual es: ({producto.cantidad_actual})",
            #     )

        ventas.total = total
        ventas.save()
        return ventas
