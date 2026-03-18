from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q, Sum
from .forms import PaqueteForm
from .models import Paquete, EstadoPaquete, Cliente


def registro_paquete(request):
    """
    Permite a un empleado registrar un nuevo paquete en el sistema.
    Asigna automáticamente el empleado actual y el estado inicial 'Recepcionado'.
    """
    if request.method == 'POST':
        form = PaqueteForm(request.POST, request.FILES)
        if form.is_valid():
            paquete = form.save(commit=False)
            paquete.empleado = request.user.empleado_profile
            paquete.estado = EstadoPaquete.objects.get(nombre_estado='Recepcionado')
            paquete.save()
            return redirect('seguimiento_paquetes')
    else:
        form = PaqueteForm()

    return render(request, 'registro/crear_envio.html', {'form': form})


def listar_paquetes(request):
    """
    Lista todos los paquetes con filtros opcionales por fecha y cliente.
    Muestra el total de ganancias acumuladas según el filtro aplicado.
    Incluye paginación de 7 registros por página.
    """
    fecha_filtro = request.GET.get('fecha')
    cliente_filtro = request.GET.get('cliente')

    paquetes = Paquete.objects.all()

    if fecha_filtro:
        paquetes = paquetes.filter(fecha_envio__date=fecha_filtro)

    if cliente_filtro:
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


def lista_paquetes_cliente(request):
    """
    Muestra al cliente autenticado únicamente sus propios paquetes registrados.
    """
    cliente = Cliente.objects.get(user=request.user)
    paquetes = Paquete.objects.filter(cliente=cliente)

    return render(request, 'registro/lista_paque.html', {'paquetes': paquetes})