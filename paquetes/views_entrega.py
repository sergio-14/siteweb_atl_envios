from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Paquete, EstadoPaquete, HistorialEstadoPaquete


def vista_seguimiento(request):
    """
    Panel de seguimiento de paquetes para empleados.
    Permite filtrar por estado y destino.
    Muestra quién realizó la entrega cuando el paquete está en estado 'Entregado'.
    """
    estado_filtro = request.GET.get('estado', '')
    destino_filtro = request.GET.get('destino', '').strip()

    paquetes = Paquete.objects.select_related(
        'cliente__user',
        'empleado__user',
        'estado'
    ).all().order_by('-fecha_envio')

    if estado_filtro:
        paquetes = paquetes.filter(estado_id=estado_filtro)

    if destino_filtro:
        paquetes = paquetes.filter(destino__icontains=destino_filtro)

    # Determinar quién entregó cada paquete en estado 'Entregado'
    for paquete in paquetes:
        paquete.entregado_por = None
        if paquete.estado.nombre_estado == 'Entregado':
            ultimo_cambio = paquete.historial_estados.filter(
                estado__nombre_estado='Entregado'
            ).order_by('-fecha_cambio').first()
            # TODO: Implementar trazabilidad del empleado en HistorialEstadoPaquete
            paquete.entregado_por = "Traza no implementada"

    estados = EstadoPaquete.objects.all()

    return render(request, 'registro/seguimiento.html', {
        'paquetes': paquetes,
        'estados': estados,
        'estado_filtro': estado_filtro,
        'destino_filtro': destino_filtro,
    })


def marcar_como_llegado(request, paquete_id):
    """
    Cambia el estado del paquete a 'Pendiente' (llegó a destino)
    y registra el cambio en el historial de estados.
    """
    paquete = get_object_or_404(Paquete, id=paquete_id)

    estado_llegado = EstadoPaquete.objects.filter(nombre_estado__iexact='Pendiente').first()

    if estado_llegado:
        paquete.estado = estado_llegado
        paquete.save()

        HistorialEstadoPaquete.objects.create(
            paquete=paquete,
            estado=estado_llegado
            # empleado=request.user.empleado_profile  # TODO: activar cuando se implemente trazabilidad
        )
        messages.success(request, f"Paquete {paquete.id} marcado como LLEGADO A DESTINO.")
    else:
        messages.error(request, "El estado 'Pendiente' no existe en la base de datos.")

    return redirect('seguimiento_paquetes')


def marcar_como_entregado(request, paquete_id):
    """
    Cambia el estado del paquete a 'Entregado' de forma definitiva.
    Redirige al listado general de paquetes.
    """
    paquete = get_object_or_404(Paquete, id=paquete_id)

    entregado_estado = EstadoPaquete.objects.get(nombre_estado="Entregado")
    paquete.estado = entregado_estado
    paquete.save()

    return redirect('listar_paquetes')


def ver_detalle_paquete(request, paquete_id):
    """
    Muestra el detalle completo de un paquete específico.
    """
    paquete = get_object_or_404(Paquete, id=paquete_id)
    return render(request, 'ver_detalle_paquete.html', {'paquete': paquete})