from rest_framework import viewsets, filters
from ..models import IngresosExternos
from ..serializers.ingresosExternosSerializer import IngresosExternosSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action
from rest_framework.response import Response


class IngresosExternosView(viewsets.ModelViewSet):
    queryset = IngresosExternos.objects.all()
    serializer_class = IngresosExternosSerializer
    
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    filter_backends = [filters.SearchFilter]
    search_fields = ['tipoIngreso']
    
    def get_queryset(self):
        return IngresosExternos.objects.all().order_by('-fecha')

    @action(detail=False, methods=['post'])
    def bulk_delete(self, request):
        ids = request.data.get('ids', [])
        self.queryset.filter(id__in=ids).delete()
        return Response(status=204)