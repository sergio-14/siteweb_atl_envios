
from django.shortcuts import render

# -- Caso de uso: Registro de Paquetes --
from .views_registro import (
    registro_paquete,
    listar_paquetes,
    lista_paquetes_cliente,
)

# -- Caso de uso: Entrega de Paquetes --
from .views_entrega import (
    vista_seguimiento,
    marcar_como_llegado,
    marcar_como_entregado,
    ver_detalle_paquete,
)

# -- Caso de uso: Reporte de Paquetes --
from .views_reportes import (
    generar_factura,
)


def home(request):
    """Vista de inicio general de la aplicación."""
    return render(request, 'home.html')