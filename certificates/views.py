import io
import qrcode
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader

from .models import CertificateRequest
from .forms import CertificateRequestForm


@login_required
def create_certificate_request(request):
    if request.method == 'POST':
        form = CertificateRequestForm(request.POST, request.FILES)
        if form.is_valid():
            cert = form.save(commit=False)
            cert.resident = request.user
            cert.save()
            messages.success(request, "Tu solicitud de certificado fue enviada exitosamente para revisión.")
            return redirect('portal:mis_certificados')
    else:
        form = CertificateRequestForm()

    return render(request, 'certificates/solicitar.html', {'form': form})


@login_required
def download_certificate_pdf(request, certificate_id):
    cert = get_object_or_404(CertificateRequest, id=certificate_id)

    # Solo el titular o administradores pueden descargarlo
    if not (request.user == cert.resident or request.user.is_staff):
        return HttpResponse("No autorizado", status=403)

    if cert.status != CertificateRequest.StatusChoices.APROBADO:
        return HttpResponse("El certificado aún no se encuentra aprobado.", status=400)

    # Configuración de canvas y página
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Encabezado institucional
    p.setFont("Helvetica-Bold", 16)
    p.drawCentredString(width / 2.0, height - 80, "JUNTA DE VECINOS - UNIDAD TERRITORIAL")
    p.setFont("Helvetica", 11)
    p.drawCentredString(width / 2.0, height - 100, "Certificado Oficial de Residencia y Domicilio")
    p.setStrokeColor(colors.HexColor("#0284C7"))
    p.setLineWidth(2)
    p.line(50, height - 115, width - 50, height - 115)

    # Cuerpo del documento
    full_name = cert.resident.get_full_name() or cert.resident.username
    text = (
        f"Por medio del presente documento, la directiva de la Junta de Vecinos certifica que "
        f"{full_name}, cédula de identidad N° {cert.resident.rut}, "
        f"mantiene residencia activa en el domicilio ubicado en: {cert.resident.address}."
    )

    text_object = p.beginText(60, height - 170)
    text_object.setFont("Helvetica", 11)
    text_object.setTextOrigin(60, height - 170)
    text_object.setLeading(18)

    for line in [
        f"Certificado emitido para fines de: {cert.purpose}.",
        "",
        text,
        "",
        "Se extiende el presente comprobante a solicitud de la persona interesada para los",
        "trámites legales, laborales o comunitarios que estime conveniente.",
    ]:
        text_object.textLine(line)
    p.drawText(text_object)

    # Generación del Código QR con URL de verificación
    verify_url = request.build_absolute_uri(f"/certificates/verify/{cert.verification_code}/")
    qr = qrcode.QRCode(box_size=3, border=1)
    qr.add_data(verify_url)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white")

    qr_buffer = io.BytesIO()
    qr_img.save(qr_buffer, format='PNG')
    qr_buffer.seek(0)

    # Estampado del QR y metadatos
    qr_reader = ImageReader(qr_buffer)
    p.drawImage(qr_reader, 60, height - 380, width=110, height=110)

    p.setFont("Helvetica-Bold", 9)
    p.drawString(185, height - 320, "VERIFICACIÓN DIGITAL:")
    p.setFont("Helvetica", 8)
    p.drawString(185, height - 335, f"Código único: {cert.verification_code}")
    emission_date = cert.issued_at.strftime('%d-%m-%Y %H:%M') if cert.issued_at else 'N/A'
    p.drawString(185, height - 350, f"Fecha de emisión: {emission_date}")
    p.drawString(185, height - 365, "Escanee el código QR para validar la autenticidad en la plataforma.")

    # Línea de firma
    p.line(width - 240, height - 330, width - 60, height - 330)
    p.setFont("Helvetica-Bold", 9)
    p.drawCentredString(width - 150, height - 345, "Firma Directiva Responsable")
    p.setFont("Helvetica", 8)
    p.drawCentredString(width - 150, height - 357, "Unidad Territorial")

    p.showPage()
    p.save()
    buffer.seek(0)
    return HttpResponse(buffer, content_type='application/pdf')


def verify_certificate_view(request, code):
    cert = get_object_or_404(CertificateRequest, verification_code=code)
    return render(request, 'certificates/verify.html', {'cert': cert})