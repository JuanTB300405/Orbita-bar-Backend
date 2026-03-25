from rest_framework import viewsets, filters
from ..serializers.notificacionesSerializer import NotificacionesSerializer;
from rest_framework.authentication import TokenAuthentication

from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

from rest_framework.permissions import IsAuthenticated
from ..models import Notificaciones

class NotificacionView(viewsets.ModelViewSet):
    
    queryset = Notificaciones.objects.filter(leida=False).order_by('-fecha')
    serializer_class = NotificacionesSerializer

    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]


    @action(detail=True, methods=['post'])
    def marcar_leida(self, request, pk=None):
        try:
            notificacion = self.get_object()
            notificacion.leida = True
            notificacion.save()
            return Response({'status': 'notificación marcada como leída'})
        except Exception as e:
            return Response({'Error': e})