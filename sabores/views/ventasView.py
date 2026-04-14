from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from django.db.models import F
from collections import defaultdict
from ..models import Ventas, DetallesVentas, Productos
from ..serializers.ventasSerializer import VentasSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication

class VentasView(viewsets.ModelViewSet):
    queryset = Ventas.objects.all()
    serializer_class = VentasSerializer

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    filter_backends = [filters.SearchFilter]
    search_fields = ['fecha', 'producto']

    @action(detail=False, methods=['post', 'delete'], url_path='bulk_delete')
    def bulk_delete(self, request):
        ids = request.data.get('ids', [])
        if not ids:
            return Response({'error': 'No se proporcionaron IDs.'}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            # Agrupar cantidades por producto para restaurar el stock
            detalles = DetallesVentas.objects.filter(idventa__in=ids)
            stock_a_restaurar = defaultdict(int)
            for detalle in detalles:
                stock_a_restaurar[detalle.idproducto_id] += detalle.cantidad

            # Restaurar stock de cada producto afectado
            for producto_id, cantidad in stock_a_restaurar.items():
                Productos.objects.filter(id=producto_id).update(
                    cantidad_actual=F('cantidad_actual') + cantidad
                )

            # Eliminar detalles primero (DO_NOTHING no hace cascade)
            DetallesVentas.objects.filter(idventa__in=ids).delete()

            # Eliminar las ventas
            deleted_count, _ = Ventas.objects.filter(id__in=ids).delete()

        return Response({'deleted': deleted_count}, status=status.HTTP_200_OK)