from rest_framework import viewsets, filters
from ..models import Compras, DetallesCompras
from ..serializers.comprasSerializer import ComprasSerializer
from ..serializers.detallesComprasSerializer import DetallesComprasSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from rest_framework.exceptions import ValidationError


class ComprasView(viewsets.ModelViewSet):
    queryset = Compras.objects.all().prefetch_related('detallesCompra')
    serializer_class = ComprasSerializer 

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    filter_backends = [filters.SearchFilter]
    # search_fields = ['estado', "email"]

    @action(detail=False, methods=['post'])
    def bulk_delete(self, request):
        ids = request.data.get('ids', [])
        compras = self.queryset.filter(id__in=ids)

        for compra in compras:
            serializer = self.get_serializer()
            serializer.delete(compra)  # Llama al método delete del serializer

        return Response(status=204)
    
    def update(self, request, pk):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            result = serializer.save()  # Esto ejecutará tu método update modificado
            return Response(result, status=result.get('code', 200))
        except ValidationError as e:
            return Response(e.detail, status=e.detail.get('code', 400))
