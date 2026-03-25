from rest_framework import serializers
from ..models import Usuario, Proveedores, Categorias
from ..models import Productos
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "password"]
        extra_kwargs = {
            'password': {'write_only': True}
        }