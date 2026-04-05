from rest_framework import serializers
from ..models import IngresosExternos

class IngresosExternosSerializer(serializers.ModelSerializer):
    class Meta:
        model = IngresosExternos
        fields = ['id','tipoIngreso', 'ganancia','fecha']
        read_only_fields = ['id','fecha']