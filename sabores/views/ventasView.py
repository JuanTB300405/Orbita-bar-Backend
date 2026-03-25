from rest_framework import viewsets, filters
from ..models import Ventas
from ..serializers.ventasSerializer import VentasSerializer;
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication

class VentasView(viewsets.ModelViewSet):
    queryset = Ventas.objects.all()
    serializer_class = VentasSerializer 

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    filter_backends = [filters.SearchFilter]
    search_fields = ['fecha', 'producto']

    # @action(detail=False, methods=['post'])
    # def bulk_delete(self, request):
    #     ids = request.data.get('ids', [])
    #     self.queryset.filter(id__in=ids).delete()
    #     return Response(status=204)