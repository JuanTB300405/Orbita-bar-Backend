from django.shortcuts import render
from  rest_framework import viewsets
from .serializer import UsuarioSerializer
from .serializer import ProductosSerializer
from .models import Usuario
from .models import Productos

class UserView(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    
class ProductoView(viewsets.ModelViewSet):
    queryset = Productos.objects.all()
    serializer_class = ProductosSerializer