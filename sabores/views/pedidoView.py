from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from django.db import transaction

from ..models import Pedido, DetallesPedido, Ventas, DetallesVentas
from ..serializers.pedidoSerializer import PedidoSerializer
from ..serializers.productosSerializer import ProductosSerializer
from ..serializers.notificacionesSerializer import NotificacionesSerializer


class PedidoView(viewsets.ModelViewSet):
    queryset = Pedido.objects.all()
    serializer_class = PedidoSerializer

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def create(self, request):
        """
        POST /pedidos/
        Body: { "mesa_id": <id>, "productos": [{ "producto_id": <id>, "cantidad": <n> }] }
        Crea el pedido con los productos iniciales y marca la mesa como no disponible.
        """
        serializer = PedidoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        mesa = serializer.validated_data['mesa']
        if not mesa.disponible:
            return Response(
                {'error': 'La mesa ya tiene un pedido activo.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        productos = request.data.get('productos', [])
        if not productos:
            return Response(
                {'error': 'Debes incluir al menos un producto para crear el pedido.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        with transaction.atomic():
            pedido = serializer.save()
            mesa.disponible = False
            mesa.save(update_fields=['disponible'])

            total = 0
            for item in productos:
                producto_id = item.get('producto_id')
                cantidad = item.get('cantidad')

                if not producto_id or not cantidad:
                    raise ValueError('Cada producto debe tener producto_id y cantidad.')

                producto = ProductosSerializer.reducir_cantidad_inventario(producto_id, int(cantidad))
                subtotal = producto.precio * int(cantidad)

                DetallesPedido.objects.create(
                    pedido=pedido,
                    producto=producto,
                    cantidad=int(cantidad),
                    subtotal=subtotal
                )
                total += subtotal
                NotificacionesSerializer.verificar_tope_minimo(producto)

            pedido.total = total
            pedido.save(update_fields=['total'])

        return Response(PedidoSerializer(pedido).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], url_path='agregar_producto')
    def agregar_producto(self, request, pk=None):
        """
        POST /pedidos/{id}/agregar_producto/
        Body: { "productos": [{ "producto_id": <id>, "cantidad": <n> }] }
        Descuenta stock y agrega los ítems al pedido.
        """
        pedido = self.get_object()

        if pedido.estado != 'pendiente':
            return Response(
                {'error': 'Solo se pueden agregar productos a pedidos pendientes.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Acepta tanto array directo [] como objeto { "productos": [] }
        if isinstance(request.data, list):
            productos = request.data
        else:
            productos = request.data.get('productos', [])

        if not productos:
            return Response(
                {'error': 'Debes enviar al menos un producto.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        with transaction.atomic():
            total_agregado = 0
            for item in productos:
                producto_id = item.get('producto_id')
                cantidad = item.get('cantidad')

                if not producto_id or not cantidad:
                    raise ValueError('Cada item debe tener producto_id y cantidad.')

                producto = ProductosSerializer.reducir_cantidad_inventario(producto_id, int(cantidad))
                subtotal = producto.precio * int(cantidad)

                DetallesPedido.objects.create(
                    pedido=pedido,
                    producto=producto,
                    cantidad=int(cantidad),
                    subtotal=subtotal
                )
                total_agregado += subtotal
                NotificacionesSerializer.verificar_tope_minimo(producto)

            pedido.total += total_agregado
            pedido.save(update_fields=['total'])

        return Response(PedidoSerializer(pedido).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['delete'], url_path='quitar_producto')
    def quitar_producto(self, request, pk=None):
        """
        DELETE /pedidos/{id}/quitar_producto/
        Body: { "detalle_id": <id> }
        Restaura el stock y elimina el ítem del pedido.
        """
        pedido = self.get_object()

        if pedido.estado != 'pendiente':
            return Response(
                {'error': 'Solo se pueden quitar productos de pedidos pendientes.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        detalle_id = request.data.get('detalle_id')
        if not detalle_id:
            return Response(
                {'error': 'detalle_id es requerido.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            detalle = DetallesPedido.objects.get(id=detalle_id, pedido=pedido)
        except DetallesPedido.DoesNotExist:
            return Response(
                {'error': 'El detalle no existe en este pedido.'},
                status=status.HTTP_404_NOT_FOUND
            )

        with transaction.atomic():
            # Restaura stock
            ProductosSerializer.aumentar_cantidad_inventario(detalle.producto_id, detalle.cantidad)

            # Recalcula total
            pedido.total -= detalle.subtotal
            pedido.save(update_fields=['total'])

            detalle.delete()

        return Response(PedidoSerializer(pedido).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='confirmar_pago')
    def confirmar_pago(self, request, pk=None):
        """
        POST /pedidos/{id}/confirmar_pago/
        Body: { "devuelta": <monto> }
        Convierte el pedido en una Venta. El stock ya fue descontado al servir.
        """
        pedido = self.get_object()

        if pedido.estado != 'pendiente':
            return Response(
                {'error': 'Solo se pueden confirmar pedidos pendientes.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        detalles = pedido.detalles.all()
        if not detalles.exists():
            return Response(
                {'error': 'El pedido no tiene productos.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        devuelta = request.data.get('devuelta', 0)

        with transaction.atomic():
            # Crea la Venta (stock ya descontado, no se toca)
            venta = Ventas.objects.create(
                total=pedido.total,
                devuelta=devuelta,
                mesaId=pedido.mesa
            )

            # Copia cada DetallesPedido como DetallesVentas
            for detalle in detalles:
                DetallesVentas.objects.create(
                    idventa=venta,
                    idproducto=detalle.producto,
                    cantidad=detalle.cantidad,
                    subtotal=detalle.subtotal
                )

            # Cierra el pedido y libera la mesa
            pedido.estado = 'pagado'
            pedido.save(update_fields=['estado'])

            mesa = pedido.mesa
            mesa.disponible = True
            mesa.save(update_fields=['disponible'])

        return Response(
            {'mensaje': 'Pago confirmado.', 'venta_id': venta.id},
            status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=['post'], url_path='cancelar')
    def cancelar(self, request, pk=None):
        """
        POST /pedidos/{id}/cancelar/
        Restaura el stock de todos los ítems y libera la mesa.
        """
        pedido = self.get_object()

        if pedido.estado != 'pendiente':
            return Response(
                {'error': 'Solo se pueden cancelar pedidos pendientes.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        with transaction.atomic():
            # Restaura stock de cada ítem
            for detalle in pedido.detalles.all():
                ProductosSerializer.aumentar_cantidad_inventario(detalle.producto_id, detalle.cantidad)

            pedido.estado = 'cancelado'
            pedido.save(update_fields=['estado'])

            mesa = pedido.mesa
            mesa.disponible = True
            mesa.save(update_fields=['disponible'])

        return Response({'mensaje': 'Pedido cancelado.'}, status=status.HTTP_200_OK)
