"""
URL configuration for administrador project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
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
    path('crear_envio/', views.crear_paquete, name='crear_envio'),
    path('listar_Registro_envios/', views.listar_paquetes, name='listar_paquetes'),
    path('paquete/<int:paquete_id>/', views.ver_detalle_paquete, name='detalle_paquete'),
    path('listapaquetess/', views.lista_paque, name='lista_paque'),
    path('cambiar_estado_paquete/<int:paquete_id>/', views.cambiar_estado_paquete, name='cambiar_estado_paquete'),
    path('factura/<int:paquete_id>/', views.generar_factura, name='generar_factura'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

