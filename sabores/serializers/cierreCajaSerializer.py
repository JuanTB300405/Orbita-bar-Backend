from rest_framework import serializers
from ..models import CierreCaja 


class CierreCajaSerializer(serializers.ModelSerializer):
    class Meta:
        model = CierreCaja
        fields = '__all__'