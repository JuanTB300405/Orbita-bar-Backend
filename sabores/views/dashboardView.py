from rest_framework.views import APIView
from ..models import Ventas
from ..models import Deudores
from ..models import IngresosExternos
from ..models import Gastos
from ..models import Compras
from django.utils import timezone
from django.db.models import Sum
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from django.db.models.functions import TruncDate
from datetime import timedelta




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
        ingresosP=  IngresosExternos.objects.filter(tipoIngreso__iexact='Propina',fecha__date=hoy).aggregate(propinas=Sum('ganancia'))
        ingresosD=  IngresosExternos.objects.filter(tipoIngreso__iexact='descorche',fecha__date=hoy).aggregate(descorches=Sum('ganancia'))
        ingresosO=  IngresosExternos.objects.filter(tipoIngreso__iexact='Otro',fecha__date=hoy).aggregate(otros=Sum('ganancia'))
        #----------------------------------------------------------------------------------------------
        #GRAFICOS
        #grafico de los ultimos 7 dias de ventas
        hace_7_dias = hoy - timedelta(days=7)
        Ventas_7=Ventas.objects.filter(fecha__date__gte=hace_7_dias).annotate(dia=TruncDate('fecha')).values('dia').annotate(total=Sum('total')).order_by('dia')
        #GRAFICO DE GATOS VS VENTAS DE LOS ULTIMOS 7 DIAS
        ingresos_externos_7=IngresosExternos.objects.filter(fecha__date__gte=hace_7_dias).annotate(dia=TruncDate('fecha')).values('dia').annotate(total=Sum('ganancia')).order_by('dia')
        gastos_7 = Gastos.objects.filter(fecha_de_pago__date__gte=hace_7_dias,estado__iexact='variable').annotate(dia=TruncDate('fecha_de_pago')).values('dia').annotate(total=Sum('precio')).order_by('dia')
        compras_7 = Compras.objects.filter(fecha__date__gte=hace_7_dias).annotate(dia=TruncDate('fecha')).values('dia').annotate(total=Sum('subtotal')).order_by('dia')
        
        Resultado={}
        
        for item in Ventas_7:
            dia=str(item['dia'])
            if dia not in Resultado:
             Resultado[dia] ={"dia":dia,"Ingresos":0,"Gastos":0}
            Resultado[dia]["Ingresos"] += item['total'] 
            
        for item in ingresos_externos_7:
            dia=str(item['dia'])
            if dia not in Resultado:
             Resultado[dia] ={"dia":dia,"Ingresos":0,"Gastos":0}
            Resultado[dia]["Ingresos"] += item['total']
            
        for item in gastos_7:
            dia=str(item['dia'])
            if dia not in Resultado:
                Resultado[dia] ={"dia":dia,"Ingresos":0,"Gastos":0}
            Resultado[dia]["Gastos"] += item['total']
            
        for item in compras_7:
            dia=str(item['dia'])
            if dia not in Resultado:
                Resultado[dia] ={"dia":dia,"Ingresos":0,"Gastos":0}
            Resultado[dia]["Gastos"] += item['total']


        
        return Response({
                "success": True,
                "ventas_hoy": ventas['ventas_hoy'] if ventas['ventas_hoy'] is not None else 0,
                "conteo_deudores": conteo,
                "deuda_total": total_deuda['deuda'] if total_deuda['deuda'] is not None else 0,
                "propinas": ingresosP['propinas'] if ingresosP['propinas'] is not None else 0,
                "descorches": ingresosD['descorches'] if ingresosD['descorches'] is not None else 0,
                "otros": ingresosO['otros'] if ingresosO['otros'] is not None else 0,
                "graficoVentas7":Ventas_7,
                "graficoGastosVsIngresos":list(Resultado.values())
            }, status=status.HTTP_200_OK)
      except Exception as e:
        return Response({
                "success": False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        