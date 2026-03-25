from rest_framework import serializers
from ..models import Usuario, Proveedores
from ..models import Gastos
from django.contrib.auth.models import User

        
class GastosSerializer(serializers.ModelSerializer):

    class Meta:
        model = Gastos
        fields = '__all__'


    # def validate(self, data):
    #     nombre = data.get('nombre')
        
    #     instance_id = self.instance.id if self.instance else None

    #     if Productos.objects.filter(
    #         nombre=nombre, categoria=categoria, proveedorid=proveedorid
    #     ).exclude(id=instance_id).exists():
    #         raise serializers.ValidationError("Ya existe un producto con ese nombre, categoría y proveedor.")
        
    #     return data
    