from rest_framework import viewsets, filters
from ..models import Productos
from ..serializers.productosSerializer import ProductosSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status


class ProductoView(viewsets.ModelViewSet):
    queryset = Productos.objects.select_related("proveedorid").all()
    serializer_class = ProductosSerializer

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    filter_backends = [filters.SearchFilter]
    search_fields = ['nombre', 'categoriaid__nombre', "proveedorid__nombre"] # ''

    @action(detail=False, methods=['POST'])
    def eliminar_productos(self, request):
        try:

            ids = request.data["ids"];

            if not isinstance(ids, list):
                return Response({"error": "Debes enviar una lista de IDs."}, status=status.HTTP_400_BAD_REQUEST)

            productos_filtrados = Productos.objects.filter(id__in=ids)
            conteo_productos_filtrados = productos_filtrados.count()

            productos_filtrados.delete();

            return Response({"message": f"Se han eliminado correctamente {conteo_productos_filtrados} productos"}, status=status.HTTP_204_NO_CONTENT);
    
        except Exception as e:
            return Response({'Error': e})