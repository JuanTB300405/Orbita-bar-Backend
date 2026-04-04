from  rest_framework import viewsets, filters
from ..models import Deudores
from ..serializers.deudoresSerializer import DeudoresSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication

class DeudoresView(viewsets.ModelViewSet):
    queryset = Deudores.objects.all()
    serializer_class = DeudoresSerializer
    
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    filter_backends = [filters.SearchFilter]
    # Permite buscar por nombre o celular
    search_fields = ['nombre', 'celular']
    
    def get_queryset(self):
        queryset = Deudores.objects.all().order_by('-fecha')
        
        #filtro adicional por autorizacion
        autorizacion = self.request.query_params.get('autorizacion')
        if autorizacion is not None:
            queryset = queryset.filter(autorizacion=autorizacion.lower() == 'true' )
            
        return queryset