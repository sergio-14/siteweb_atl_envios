from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import mm
from .models import Paquete


def generar_factura(request, paquete_id):
    """
    Genera una factura en formato PDF estilo ticket (80mm de ancho) 
    para el paquete indicado. El documento se muestra inline en el navegador.
    """
    paquete = get_object_or_404(Paquete, id=paquete_id)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="factura_{paquete.id}.pdf"'

    # Configuración de página estilo ticket
    ancho_ticket = 80 * mm
    alto_ticket = 200 * mm
    p = canvas.Canvas(response, pagesize=(ancho_ticket, alto_ticket))

    x = 5 * mm
    y = alto_ticket - 10 * mm

    # Título
    p.setFont("Helvetica-Bold", 14)
    p.drawCentredString(ancho_ticket / 2, y, "FACTURA DE ENVÍO")
    y -= 10 * mm

    # Línea divisoria superior
    p.line(x, y, ancho_ticket - x, y)
    y -= 8 * mm

    def dibujar_linea(label, value, y_pos):
        """Dibuja una fila de etiqueta-valor dentro del ticket."""
        p.setFont("Helvetica-Bold", 10)
        p.drawString(x, y_pos, label)
        p.setFont("Helvetica", 10)
        p.drawString(x + 25 * mm, y_pos, str(value))
        return y_pos - 6 * mm

    # Datos del paquete
    y = dibujar_linea("ID Paquete:", paquete.id, y)
    y = dibujar_linea("Cliente:", paquete.cliente.user.get_full_name(), y)
    y = dibujar_linea("CI:", paquete.cliente.ci, y)
    y = dibujar_linea("Fecha:", paquete.fecha_envio.strftime('%d/%m/%Y %H:%M'), y)

    y -= 4 * mm
    p.line(x, y, ancho_ticket - x, y)
    y -= 6 * mm

    # Descripción del paquete
    p.setFont("Helvetica", 10)
    p.drawString(x, y, "Detalle:")
    y -= 5 * mm
    p.setFont("Helvetica-Oblique", 9)
    p.drawString(x + 2 * mm, y, f" {paquete.descripcion}")
    y -= 5 * mm

    # Destino y dirección
    p.setFont("Helvetica", 10)
    p.drawString(x, y, f"Destino: {paquete.destino}")
    y -= 5 * mm
    p.drawString(x, y, f"Dir: {paquete.direccion_destino}")

    y -= 8 * mm
    p.line(x, y, ancho_ticket - x, y)
    y -= 8 * mm

    # Total a pagar
    p.setFont("Helvetica-Bold", 12)
    p.drawString(x, y, "TOTAL:")
    p.drawRightString(ancho_ticket - x, y, f"{paquete.precio} Bs.")

    p.showPage()
    p.save()

    return response