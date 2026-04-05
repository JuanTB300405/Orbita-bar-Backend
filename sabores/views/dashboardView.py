from rest_framework.views import APIView
from ..models import Ventas
from ..models import Deudores
from ..models import IngresosExternos
from django.utils import timezone
from django.db.models import Sum
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication



class DashboardView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    def get (self,request):
      try:
        #VENTAS DIARIAS
        hoy= timezone.now().date() 
        #filtro las ventas por el dia de hoy y sumo de una vez su total para mostrarlo en el dashboard
        ventas= Ventas.objects.filter(fecha__date=hoy).aggregate(ventas_hoy=Sum('total'))
        #----------------------------------------------------------------------------------------------
        #DEUDORES
        #conteo deudores y total deuda
        conteo= Deudores.objects.count()
        total_deuda= Deudores.objects.all().aggregate(deuda=Sum('deuda'))
        #----------------------------------------------------------------------------------------------
        #INGRESOS EXTERNOS
        ingresosP=  IngresosExternos.objects.filter(tipoIngreso__iexact='Propina').aggregate(propinas=Sum('ganancia'))
        ingresosD=  IngresosExternos.objects.filter(tipoIngreso__iexact='descorche').aggregate(descorches=Sum('ganancia'))
        ingresosO=  IngresosExternos.objects.filter(tipoIngreso__iexact='Otro').aggregate(otros=Sum('ganancia'))
        
        
        
        return Response({
                "success": True,
                "ventas_hoy": ventas['ventas_hoy'] if ventas['ventas_hoy'] is not None else 0,
                "conteo_deudores": conteo,
                "deuda_total": total_deuda['deuda'] if total_deuda['deuda'] is not None else 0,
                "propinas": ingresosP['propinas'] if ingresosP['propinas'] is not None else 0,
                "descorches": ingresosD['descorches'] if ingresosD['descorches'] is not None else 0,
                "otros": ingresosO['otros'] if ingresosO['otros'] is not None else 0
            }, status=status.HTTP_200_OK)
      except Exception as e:
        return Response({
                "success": False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        