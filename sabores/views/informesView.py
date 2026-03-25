from rest_framework import viewsets, filters
from ..models import Compras, DetallesCompras, Ventas, DetallesVentas, Productos
from ..serializers.comprasSerializer import ComprasSerializer
from ..serializers.detallesComprasSerializer import DetallesComprasSerializer
from ..serializers.ventasSerializer import VentasSerializer
from ..serializers.detallesVentasSerializer import DetallesVentasSerializer
from ..serializers.productosSerializer import ProductosSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from rest_framework.exceptions import ValidationError

class InformesView(viewsets.ModelViewSet):
    serializer_class = ProductosSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        productos = Productos.objects.select_related('proveedorid').all()
        try:
            informe_productos = []
            for p in productos:
                if p.cantidad_inicial > 0 and (p.cantidad_inicial != p.cantidad_actual):
                    porcentaje_vendido = round(((p.cantidad_inicial - p.cantidad_actual)/p.cantidad_inicial)*100)
                else:
                    porcentaje_vendido = 0

                informe_productos.append({
                    "nombre": p.nombre,
                    "cantidad_actual": p.cantidad_actual,
                    "estado": f"{porcentaje_vendido}",
                    "proveedor": p.proveedorid.nombre if p.proveedorid else None
                })
            return Response({
                "success": True,
                "data": informe_productos
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "success": False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
