from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .forms import PaqueteForm
from .models import Paquete, EstadoPaquete,Cliente
from django.core.paginator import Paginator
from django.db.models import Sum


def home(request):
    return render(request, 'home.html')

def crear_paquete(request):
    if request.method == 'POST':
        form = PaqueteForm(request.POST, request.FILES)
        if form.is_valid():
            paquete = form.save(commit=False)  # No guardes aún en la base de datos
            paquete.empleado = request.user.empleado_profile  # Asigna el empleado como el usuario actual
            paquete.estado = EstadoPaquete.objects.get(nombre_estado='Recepcionado')  # Asigna el estado inicial
            paquete.save()  # Ahora guarda en la base de datos
            return redirect('seguimiento_paquetes') 
    else:
        form = PaqueteForm()
    
    return render(request, 'registro/crear_envio.html', {'form': form})

from django.db.models import Q, Sum

def listar_paquetes(request):
    fecha_filtro = request.GET.get('fecha')  
    cliente_filtro = request.GET.get('cliente')
    paquetes = Paquete.objects.all()

    if fecha_filtro:
        paquetes = paquetes.filter(fecha_envio__date=fecha_filtro)

    if cliente_filtro:
        # Filtra si el nombre CONTIENE el texto O si el CI CONTIENE el texto
        paquetes = paquetes.filter(
            Q(cliente__user__first_name__icontains=cliente_filtro) | 
            Q(cliente__ci=cliente_filtro)
        )

    total_ganancias = paquetes.aggregate(Sum('precio'))['precio__sum'] or 0

    paginator = Paginator(paquetes, 7)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'registro/listar_paquetes.html', {
        'paquetes': page_obj,
        'total_ganancias': total_ganancias,
        'fecha_filtro': fecha_filtro,
        'cliente_filtro': cliente_filtro,
    })


def vista_seguimiento(request):
    # Parámetros de filtro
    estado_filtro = request.GET.get('estado', '')
    destino_filtro = request.GET.get('destino', '').strip()

    # Consulta base con relaciones necesarias
    paquetes = Paquete.objects.select_related(
        'cliente__user', 
        'empleado__user', 
        'estado'
    ).all().order_by('-fecha_envio')

    # Aplicar filtros
    if estado_filtro:
        paquetes = paquetes.filter(estado_id=estado_filtro)
    
    if destino_filtro:
        paquetes = paquetes.filter(destino__icontains=destino_filtro)

    # --- LÓGICA PARA "QUIÉN LO ENTREGO" ---
    # Necesitamos buscar en el historial el último cambio a 'Entregado'
    for paquete in paquetes:
        paquete.entregado_por = None
        if paquete.estado.nombre_estado == 'Entregado':
            ultimo_cambio = paquete.historial_estados.filter(
                estado__nombre_estado='Entregado'
            ).order_by('-fecha_cambio').first()
            
            # Asumiendo que HistorialEstadoPaquete necesita un campo 'empleado' 
            # para saber quién hizo el cambio. Si no lo tienes, este campo saldrá vacío.
            # paquete.entregado_por = ultimo_cambio.empleado if ultimo_cambio else "N/A"
            paquete.entregado_por = "Traza no implementada" # Temporalmente

    # Datos para filtros
    estados = EstadoPaquete.objects.all()

    return render(request, 'registro/seguimiento.html', {
        'paquetes': paquetes,
        'estados': estados,
        'estado_filtro': estado_filtro,
        'destino_filtro': destino_filtro,
    })

from .models import Paquete, HistorialEstadoPaquete, EstadoPaquete
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
def marcar_como_llegado(request, paquete_id):
    paquete = get_object_or_404(Paquete, id=paquete_id)
    
    # Buscamos el estado 'Pendiente' (o el nombre que tengas para cuando llega a destino)
    # AJUSTA ESTE NOMBRE SI TU ESTADO SE LLAMA DIFERENTE
    estado_llegado = EstadoPaquete.objects.filter(nombre_estado__iexact='Pendiente').first()
    
    if estado_llegado:
        # 1. Actualizar estado actual del paquete
        paquete.estado = estado_llegado
        paquete.save()
        
        # 2. Registrar en el historial
        HistorialEstadoPaquete.objects.create(
            paquete=paquete,
            estado=estado_llegado
            # empleado=request.user.empleado_profile  # Si tienes implementado el seguimiento de empleado
        )
        messages.success(request, f"Paquete {paquete.id} marcado como LLEGADO A DESTINO.")
    else:
        messages.error(request, "El estado 'Pendiente' no existe en la base de datos.")
        
    return redirect('seguimiento_paquetes')

def ver_detalle_paquete(request, paquete_id):
    paquete = get_object_or_404(Paquete, id=paquete_id)
    return render(request, 'ver_detalle_paquete.html', {'paquete': paquete})


def lista_paque(request):
   
    cliente = Cliente.objects.get(user=request.user)
    
    paquetes = Paquete.objects.filter(cliente=cliente)
    
    return render(request, 'registro/lista_paque.html', {'paquetes': paquetes})

from .models import Paquete, EstadoPaquete

def cambiar_estado_paquete(request, paquete_id):
    paquete = get_object_or_404(Paquete, id=paquete_id)
   
    entregado_estado = EstadoPaquete.objects.get(nombre_estado="Entregado")
    paquete.estado = entregado_estado
    paquete.save()

    return redirect('listar_paquetes') 

from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from .models import Paquete

from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import mm
from .models import Paquete

def generar_factura(request, paquete_id):
    paquete = get_object_or_404(Paquete, id=paquete_id)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="factura_{paquete.id}.pdf"'

    # --- CONFIGURACIÓN DE PÁGINA (Estilo Ticket) ---
    # Ancho 80mm, Alto ajustable (ej. 200mm)
    ancho_ticket = 80 * mm
    alto_ticket = 200 * mm 
    p = canvas.Canvas(response, pagesize=(ancho_ticket, alto_ticket))
    
    # Coordenadas iniciales (margen izquierdo pequeño)
    x = 5 * mm
    y = alto_ticket - 10 * mm
    
    # --- CONTENIDO DE LA FACTURA ---
    # Título
    p.setFont("Helvetica-Bold", 14)
    p.drawCentredString(ancho_ticket / 2, y, "FACTURA DE ENVÍO")
    y -= 10 * mm

    # Línea divisoria
    p.line(x, y, ancho_ticket - x, y)
    y -= 8 * mm

    # Detalles
    p.setFont("Helvetica", 10)
    
    def dibujar_linea(label, value, y_pos):
        p.setFont("Helvetica-Bold", 10)
        p.drawString(x, y_pos, label)
        p.setFont("Helvetica", 10)
        p.drawString(x + 25 * mm, y_pos, str(value))
        return y_pos - 6 * mm

    y = dibujar_linea("ID Paquete:", paquete.id, y)
    y = dibujar_linea("Cliente:", paquete.cliente.user.get_full_name(), y)
    y = dibujar_linea("CI:", paquete.cliente.ci, y)
    y = dibujar_linea("Fecha:", paquete.fecha_envio.strftime('%d/%m/%Y %H:%M'), y)
    
    y -= 4 * mm
    p.line(x, y, ancho_ticket - x, y)
    y -= 6 * mm
    
    # Descripción y Destino (con salto de línea si es necesario)
    p.drawString(x, y, "Detalle:")
    y -= 5 * mm
    p.setFont("Helvetica-Oblique", 9)
    p.drawString(x + 2 * mm, y, f" {paquete.descripcion}")
    y -= 5 * mm
    
    p.setFont("Helvetica", 10)
    p.drawString(x, y, f"Destino: {paquete.destino}")
    y -= 5 * mm
    p.drawString(x, y, f"Dir: {paquete.direccion_destino}")
    
    y -= 8 * mm
    p.line(x, y, ancho_ticket - x, y)
    y -= 8 * mm

    # Precio Total
    p.setFont("Helvetica-Bold", 12)
    p.drawString(x, y, "TOTAL:")
    p.drawRightString(ancho_ticket - x, y, f"{paquete.precio} Bs.")

    p.showPage()
    p.save()

    return response