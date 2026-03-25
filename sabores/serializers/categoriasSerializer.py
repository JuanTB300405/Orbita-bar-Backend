from rest_framework import serializers
from ..models import Categorias
        
class CategoriasSerializer(serializers.ModelSerializer):

    class Meta:
        model = Categorias
        fields = ["id","nombre"]

    def validate(self, data):
        try:
            nombre = data.get('nombre')
            
            instance_id = self.instance.id if self.instance else None

            if Categorias.objects.filter(
                nombre=nombre).exclude(id=instance_id).exists():
                raise serializers.ValidationError("Ya existe una categoría con ese nombre")

            return data
        except Exception as e:
            raise e