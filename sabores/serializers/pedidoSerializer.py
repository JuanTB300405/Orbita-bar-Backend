from rest_framework import serializers
from ..models import Pedido, DetallesPedido, Productos, Mesa
from .productosSerializer import ProductosSerializer
from .mesaSerializer import MesaSerializer


class DetallesPedidoSerializer(serializers.ModelSerializer):
    producto_id = serializers.PrimaryKeyRelatedField(
        queryset=Productos.objects.all(), write_only=True, source='producto'
    )
    producto = ProductosSerializer(read_only=True)

    class Meta:
        model = DetallesPedido
        fields = ['id', 'producto_id', 'producto', 'cantidad', 'subtotal']


class PedidoSerializer(serializers.ModelSerializer):
    mesa_id = serializers.PrimaryKeyRelatedField(
        queryset=Mesa.objects.all(), write_only=True, source='mesa', required=False, allow_null=True
    )
    mesa = MesaSerializer(read_only=True)
    detalles = DetallesPedidoSerializer(many=True, read_only=True)

    class Meta:
        model = Pedido
        fields = ['id', 'mesa_id', 'mesa', 'estado', 'fecha_creacion', 'total', 'proveniencia', 'detalles']
