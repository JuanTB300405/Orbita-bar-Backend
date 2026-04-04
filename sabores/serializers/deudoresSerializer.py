from rest_framework import serializers
from ..models import Deudores

class DeudoresSerializer(serializers.ModelSerializer):

    class Meta:
        model = Deudores
        fields = ['id', 'nombre', 'celular', 'deuda', 'fecha', 'autorizacion']
        read_only_fields = ['id', 'fecha']

    def validate_autorizacion(self, value):
        # El cliente debe autorizar el registro de sus datos
        if value is False:
            raise serializers.ValidationError("El cliente no autorizó el registro de sus datos")
        return value