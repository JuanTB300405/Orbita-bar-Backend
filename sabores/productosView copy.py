from .serializers.productosSerializer import ProductosSerializer
from rest_framework.decorators import api_view, authentication_classes, permission_classes, action
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework import status, viewsets, filters
from .models import Productos
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication


class ProductoView(viewsets.ModelViewSet):
    serializer_class = ProductosSerializer
    queryset = Productos.objects.all()
    filter_backends = [filters.SearchFilter]
    search_fields = ["nombre", "categoria", "proveedor"]
    authentication_classes = TokenAuthentication
    permission_classes = IsAuthenticated

    # @api_view(['GET'])
    @action(detail=True, methods=['get'])
    def buscar_productos(request):
        print(request.query_params.dict())
        if request.query_params:
            productos = Productos.objects.filter(**request.query_params.dict())

        else:
            productos = Productos.objects.all()

        if productos:
            productosSerializer = ProductosSerializer(productos, many=True)
            return Response({"productos": productosSerializer.data}, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)
        

    # @api_view(['GET'])
    @action(detail=True, methods=['get'])
    def buscar_productos_por_campo(request):
        print(request.query_params.dict())
        if request.query_params:
            productos = Productos.objects.filter(**request.query_params.dict())

        else:
            productos = Productos.objects.all()

        if productos:
            productosSerializer = ProductosSerializer(productos, many=True)
            return Response({"productos": productosSerializer.data}, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)
        

    # @api_view(['POST'])
    @action(detail=True, methods=['post'])
    def crear_producto(request, view):

        productosSerializer = ProductosSerializer(data=request.data)
        
        if productosSerializer.is_valid():
            productosSerializer.save()
            return Response({"producto": productosSerializer.data}, status=status.HTTP_201_CREATED)
        else:
            return Response(productosSerializer.errors, status=status.HTTP_400_BAD_REQUEST)


    # @api_view(['PUT'])
    @action(detail=True, methods=['put'])
    def actualizar_producto(request, id):
        producto = Productos.objects.get(id=id)
        productoSerializer = ProductosSerializer(instance=producto, data=request.data, partial=True)
    
        if productoSerializer.is_valid():
            productoSerializer.save()
            return Response({"producto": productoSerializer.data}, status=status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        
    # @api_view(['DELETE'])
    @action(detail=True, methods=['delete'])
    def eliminar_producto(request, id):
        producto = get_object_or_404(Productos, id=id)
        producto.delete()
        return Response({"mesagge": "producto eliminado exitosamente"}, status=status.HTTP_202_ACCEPTED)