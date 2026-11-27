
import io
from pathlib import Path

import qrcode

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader, simpleSplit

from .models import CertificateRequest
from .forms import CertificateRequestForm


# ======================================================
# SOLICITAR CERTIFICADO
# ======================================================

@login_required
def create_certificate_request(request):

    if request.method == "POST":

        form = CertificateRequestForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():

            cert = form.save(commit=False)
            cert.resident = request.user
            cert.save()

            messages.success(
                request,
                "Tu solicitud de certificado fue enviada "
                "exitosamente para revisión."
            )

            return redirect("portal:mis_certificados")

    else:
        form = CertificateRequestForm()

    return render(
        request,
        "certificates/solicitar.html",
        {"form": form}
    )


# ======================================================
# GENERAR CERTIFICADO PDF
# ======================================================

@login_required
def download_certificate_pdf(request, certificate_id):

    cert = get_object_or_404(
        CertificateRequest,
        id=certificate_id
    )

    # Solo titular o personal autorizado
    if not (
        request.user == cert.resident
        or request.user.is_staff
        or request.user.is_superuser
    ):
        return HttpResponse(
            "No autorizado",
            status=403
        )

    # Debe estar aprobado
    if cert.status != CertificateRequest.StatusChoices.APROBADO:
        return HttpResponse(
            "El certificado aún no se encuentra aprobado.",
            status=400
        )

    buffer = io.BytesIO()

    pdf = canvas.Canvas(
        buffer,
        pagesize=letter
    )

    width, height = letter

    margen = 55
    ancho_texto = width - (margen * 2)

    azul = colors.HexColor("#0284C7")
    oscuro = colors.HexColor("#0F172A")
    gris = colors.HexColor("#475569")

    # ==================================================
    # ENCABEZADO
    # ==================================================

    pdf.setFillColor(oscuro)
    pdf.setFont("Helvetica-Bold", 15)

    pdf.drawCentredString(
        width / 2,
        height - 75,
        "JUNTA DE VECINOS - UNIDAD TERRITORIAL"
    )

    pdf.setFont("Helvetica", 11)

    pdf.drawCentredString(
        width / 2,
        height - 96,
        "CERTIFICADO DE RESIDENCIA Y DOMICILIO"
    )

    pdf.setStrokeColor(azul)
    pdf.setLineWidth(2)

    pdf.line(
        margen,
        height - 115,
        width - margen,
        height - 115
    )

    # ==================================================
    # DATOS DEL CERTIFICADO
    # ==================================================

    nombre = (
        cert.resident.get_full_name()
        or cert.resident.username
    )

    rut = cert.resident.rut
    domicilio = cert.resident.address
    finalidad = cert.purpose

    pdf.setFillColor(oscuro)

    # Finalidad con salto automático de línea
    y = height - 165

    lineas_finalidad = simpleSplit(
        f"Certificado emitido para fines de: {finalidad}.",
        "Helvetica",
        11,
        ancho_texto
    )

    pdf.setFont("Helvetica", 11)

    for linea in lineas_finalidad:
        pdf.drawString(margen, y, linea)
        y -= 18

    y -= 25

    # Texto principal
    texto = (
        "Por medio del presente documento, la directiva "
        "de la Junta de Vecinos certifica que "
        f"{nombre}, cédula de identidad N° {rut}, "
        "mantiene residencia activa en el domicilio "
        f"ubicado en: {domicilio}."
    )

    lineas = simpleSplit(
        texto,
        "Helvetica",
        11,
        ancho_texto
    )

    pdf.setFont("Helvetica", 11)

    for linea in lineas:
        pdf.drawString(margen, y, linea)
        y -= 19

    y -= 25

    cierre = (
        "Se extiende el presente comprobante a solicitud "
        "de la persona interesada para los trámites "
        "legales, laborales o comunitarios que estime "
        "conveniente."
    )

    lineas_cierre = simpleSplit(
        cierre,
        "Helvetica",
        11,
        ancho_texto
    )

    for linea in lineas_cierre:
        pdf.drawString(margen, y, linea)
        y -= 19

    # ==================================================
    # CÓDIGO QR
    # ==================================================

    verify_url = request.build_absolute_uri(
        f"/certificates/verify/{cert.verification_code}/"
    )

    qr = qrcode.QRCode(
        box_size=4,
        border=2
    )

    qr.add_data(verify_url)
    qr.make(fit=True)

    qr_img = qr.make_image(
        fill_color="black",
        back_color="white"
    )

    qr_buffer = io.BytesIO()
    qr_img.save(qr_buffer, format="PNG")
    qr_buffer.seek(0)

    qr_reader = ImageReader(qr_buffer)

    # Zona inferior reservada para QR y firma
    qr_y = 255

    pdf.drawImage(
        qr_reader,
        55,
        qr_y,
        width=110,
        height=110
    )

    # ==================================================
    # INFORMACIÓN DE VERIFICACIÓN
    # ==================================================

    pdf.setFillColor(oscuro)
    pdf.setFont("Helvetica-Bold", 9)

    pdf.drawString(
        180,
        345,
        "VERIFICACIÓN DIGITAL"
    )

    pdf.setFont("Helvetica", 7)

    pdf.drawString(
        180,
        328,
        f"Código: {cert.verification_code}"
    )

    fecha = (
        cert.issued_at.strftime("%d/%m/%Y %H:%M")
        if cert.issued_at
        else "No disponible"
    )

    pdf.drawString(
        180,
        312,
        f"Emisión: {fecha}"
    )

    pdf.drawString(
        180,
        296,
        "Escanee el código QR"
    )

    pdf.drawString(
        180,
        284,
        "para verificar su autenticidad."
    )

    # ==================================================
    # FIRMA DE DIRECTIVA
    # ==================================================

    firma_path = (
        Path(settings.BASE_DIR)
        / "private"
        / "firma_directiva.png"
    )

    # Datos de la persona autorizada
    nombre_firmante = getattr(
        settings,
        "CERTIFICATE_SIGNER_NAME",
        "Directiva Responsable"
    )

    cargo_firmante = getattr(
        settings,
        "CERTIFICATE_SIGNER_ROLE",
        "Junta de Vecinos"
    )

    firma_centro = 465

    if firma_path.is_file():

        pdf.drawImage(
            str(firma_path),
            405,
            310,
            width=120,
            height=60,
            preserveAspectRatio=True,
            anchor="c",
            mask="auto"
        )

    # Línea de firma
    pdf.setStrokeColor(oscuro)
    pdf.setLineWidth(0.8)

    pdf.line(
        395,
        296,
        535,
        296
    )

    # Nombre y cargo
    pdf.setFillColor(oscuro)
    pdf.setFont("Helvetica-Bold", 8)

    pdf.drawCentredString(
        firma_centro,
        282,
        nombre_firmante
    )

    pdf.setFont("Helvetica", 8)

    pdf.drawCentredString(
        firma_centro,
        270,
        cargo_firmante
    )

    # ==================================================
    # PIE DE PÁGINA
    # ==================================================

    pdf.setStrokeColor(colors.HexColor("#CBD5E1"))

    pdf.line(
        margen,
        90,
        width - margen,
        90
    )

    pdf.setFillColor(gris)
    pdf.setFont("Helvetica", 8)

    pdf.drawCentredString(
        width / 2,
        75,
        "Documento emitido mediante el Sistema de Gestión Vecinal"
    )

    pdf.drawCentredString(
        width / 2,
        62,
        "La autenticidad puede comprobarse mediante el código QR."
    )

    # Guardar PDF
    pdf.showPage()
    pdf.save()

    buffer.seek(0)

    response = HttpResponse(
        buffer.getvalue(),
        content_type="application/pdf"
    )

    response["Content-Disposition"] = (
        f'inline; filename="certificado_{cert.id}.pdf"'
    )

    return response


# ======================================================
# VERIFICAR CERTIFICADO
# ======================================================

def verify_certificate_view(request, code):

    cert = get_object_or_404(
        CertificateRequest,
        verification_code=code
    )

    return render(
        request,
        "certificates/verify.html",
        {"cert": cert}
    )
