from rest_framework import viewsets, filters
from ..models import Categorias
from ..serializers.categoriasSerializer import CategoriasSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status


class CategoriasView(viewsets.ModelViewSet):
    queryset = Categorias.objects.all()
    serializer_class = CategoriasSerializer 

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    filter_backends = [filters.SearchFilter]
    search_fields = ['nombre'] # ''


    @action(detail=False, methods=['post'])
    def bulk_delete(self, request):
        ids = request.data.get('ids', [])
        self.queryset.filter(id__in=ids).delete()
        return Response(status=204)
    
    # @action(detail=False, methods=['POST'])
    # def eliminar_productos(self, request):

    #     ids = request.data["ids"];

    #     if not isinstance(ids, list):
    #         return Response({"error": "Debes enviar una lista de IDs."}, status=status.HTTP_400_BAD_REQUEST)

    #     productos_filtrados = Gastos.objects.filter(id__in=ids)
    #     conteo_productos_filtrados = productos_filtrados.count()

    #     productos_filtrados.delete();

    #     return Response({"message": f"Se han eliminado correctamente {conteo_productos_filtrados} productos"}, status=status.HTTP_204_NO_CONTENT);