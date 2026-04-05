from rest_framework import routers
from django.urls import path,include

from sabores.views import authView, comprasView, productosView, gastosView, proveedoresView, categoriasView, ventasView, notificacionesView, detallesComprasView, informesView, mesaView, deudoresView, ingresosExternosView,dashboardView


router = routers.DefaultRouter()
router.register(r'productos', productosView.ProductoView ,'productos')
router.register(r'usuarios', authView.UserView,'usuarios')
router.register(r'gastos', gastosView.GastoView,'gastos')
router.register(r'proveedores', proveedoresView.ProveedoresView,'proveedores')
router.register(r'categorias', categoriasView.CategoriasView,'categorias')
router.register(r'compras', comprasView.ComprasView,'compras')
router.register(r'detallesCompras', detallesComprasView.DetallesComprasView,'detallesCompras')
router.register(r'ventas', ventasView.VentasView,'ventas')
router.register(r'notificaciones', notificacionesView.NotificacionView)
router.register(r'informes', informesView.InformesView,'informes')
router.register(r'mesas', mesaView.MesaView,'mesas')
router.register(r'deudores', deudoresView.DeudoresView,'deudores')
router.register(r'ingresosExternos', ingresosExternosView.IngresosExternosView,'ingresosExternos')


urlpatterns = [
    path("api/v1/",include(router.urls)),
    path("api/v1/dashboard/",dashboardView.DashboardView.as_view(), name="dashboard"),
]