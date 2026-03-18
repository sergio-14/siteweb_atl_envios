from django.contrib import admin
from django.urls import path
from paquetes import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('', views.home, name='home'), 
    path('crear_envio/', views.registro_paquete, name='crear_envio'),
    path('listar_Registro_envios/', views.listar_paquetes, name='listar_paquetes'),
    path('paquete/<int:paquete_id>/', views.ver_detalle_paquete, name='detalle_paquete'),
    path('listapaquetess/', views.lista_paquetes_cliente, name='lista_paque'),         # ← cambió
    path('cambiar_estado_paquete/<int:paquete_id>/', views.marcar_como_entregado, name='cambiar_estado_paquete'),  # ← cambió
    path('factura/<int:paquete_id>/', views.generar_factura, name='generar_factura'),
    path('seguimiento/', views.vista_seguimiento, name='seguimiento_paquetes'),
    path('marcar-llegado/<int:paquete_id>/', views.marcar_como_llegado, name='marcar_como_llegado'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)