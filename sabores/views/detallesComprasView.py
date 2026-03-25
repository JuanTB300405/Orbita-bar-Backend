from rest_framework import viewsets, filters
from ..models import Compras, DetallesCompras
from ..serializers.comprasSerializer import ComprasSerializer
from ..serializers.detallesComprasSerializer import DetallesComprasSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import ValidationError


class DetallesComprasView(viewsets.ModelViewSet):
    queryset = DetallesCompras.objects.all()
    serializer_class = DetallesComprasSerializer 

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    filter_backends = [filters.SearchFilter]
    search_fields = ['idproducto__nombre', "idproducto__proveedorid__nombre"]

