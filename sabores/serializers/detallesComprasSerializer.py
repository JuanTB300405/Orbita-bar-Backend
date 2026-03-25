from rest_framework import serializers
from ..models import DetallesCompras,Productos, Compras
# from .comprasSerializer import ComprasSerializer
from .productosSerializer import ProductosSerializer
# from .comprasSerializer import ComprasSerializer

        
class DetallesComprasSerializer(serializers.ModelSerializer):

    idproducto = serializers.PrimaryKeyRelatedField(
        queryset=Productos.objects.all(), write_only=True) 
    producto = ProductosSerializer(source='idproducto', read_only=True)

    # idcompra = serializers.PrimaryKeyRelatedField(
    #     queryset=Compras.objects.all(), write_only=True) 
    # compra = ComprasSerializer(source='idcompra', read_only=True)

    id = serializers.IntegerField(required=False)

    class Meta:
        model = DetallesCompras
        fields = ["id", "idproducto", "producto", "cantidad"]
        read_only_fields = ['created_at']


    