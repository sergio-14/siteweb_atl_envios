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
            return redirect('listar_paquetes')  
    else:
        form = PaqueteForm()
    
    return render(request, 'registro/crear_envio.html', {'form': form})



def listar_paquetes(request):
    fecha_filtro = request.GET.get('fecha')  
    cliente_filtro = request.GET.get('cliente')
    paquetes = Paquete.objects.all()

   
    if fecha_filtro:
        paquetes = paquetes.filter(fecha_envio__date=fecha_filtro)

    if cliente_filtro:
        paquetes = paquetes.filter(
            cliente__user__first_name__icontains=cliente_filtro
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

def generar_factura(request, paquete_id):
   
    paquete = Paquete.objects.get(id=paquete_id)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="factura_{paquete.id}.pdf"'

    p = canvas.Canvas(response, pagesize=letter)

    p.drawString(100, 750, f"Factura para el Paquete: {paquete.descripcion}")
    p.drawString(100, 730, f"Cliente: {paquete.cliente.user.get_full_name()}")
    p.drawString(100, 710, f"Peso: {paquete.peso} kg")
    p.drawString(100, 690, f"Dimensiones: {paquete.dimensiones}")
    p.drawString(100, 670, f"Dirección de destino: {paquete.direccion_destino}")
    p.drawString(100, 630, f"Fecha de envío: {paquete.fecha_envio}")
    p.drawString(100, 610, f"Estado: {paquete.estado.nombre_estado}")
    p.drawString(100, 590, f"Precio: Bs {paquete.precio}")

    p.showPage()
    p.save()

    return response