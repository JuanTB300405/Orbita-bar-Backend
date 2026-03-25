from rest_framework import serializers
from ..models import Productos, DetallesVentas
# from .comprasSerializer import ComprasSerializer
from .productosSerializer import ProductosSerializer

        
class DetallesVentasSerializer(serializers.ModelSerializer):

    idproducto = serializers.PrimaryKeyRelatedField(
        queryset=Productos.objects.all(), write_only=True) 
    producto = ProductosSerializer(source='idproducto', read_only=True)

    class Meta:
        model = DetallesVentas
        fields = ["id", "idproducto", "producto", "subtotal", "cantidad"]
