from rest_framework import serializers
from ..models import Proveedores
from django.contrib.auth.models import User

        
class ProveedoresSerializer(serializers.ModelSerializer):

    class Meta:
        model = Proveedores
        fields = ["id","nombre", "telefono", "email"]

    def validate(self, data):
        nombre = data.get('nombre')
        email = data.get('email')
        telefono = data.get('telefono')#Validar que sea un numero, tambien el hecho de que un proveedor tenga varias telefonos de contacto o email
        
        instance_id = self.instance.id if self.instance else None

        if Proveedores.objects.filter(
            nombre=nombre, email=email, telefono=telefono
        ).exclude(id=instance_id).exists():
            raise serializers.ValidationError("Ya existe un proveedor con ese nombre, email y telefono.")
        
        errores = []

        # Verificación de duplicados por cada campo
        if Proveedores.objects.filter(nombre=nombre).exclude(id=instance_id).exists():
            errores.append("nombre")

        if Proveedores.objects.filter(email=email).exclude(id=instance_id).exists():
            errores.append("email")

        if Proveedores.objects.filter(telefono=telefono).exclude(id=instance_id).exists():
            errores.append("teléfono")

        if errores:
            campos = ", ".join(errores)
            raise serializers.ValidationError(f"Ya existe un proveedor con el mismo {campos}.")

                
        return data
    