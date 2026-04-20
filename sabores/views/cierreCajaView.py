from ..models import CierreCaja
from ..serializers.cierreCajaSerializer import CierreCajaSerializer
from rest_framework.mixins  import ListModelMixin, CreateModelMixin
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication


class CierreCajaView(ListModelMixin, CreateModelMixin, GenericViewSet):
    queryset = CierreCaja.objects.all()
    serializer_class = CierreCajaSerializer

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]