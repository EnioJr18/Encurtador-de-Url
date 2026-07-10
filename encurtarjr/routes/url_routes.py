from io import BytesIO

import qrcode
from flask import Blueprint, redirect, render_template, request, send_file
from flask_login import current_user, login_required

from encurtarjr.extensions import limiter
from encurtarjr.models import URL
from encurtarjr.services.url_service import registrar_clique


url_bp = Blueprint("urls", __name__)


@url_bp.route("/urls")
@login_required
def listar_urls():
    urls = URL.query.filter_by(user_id=current_user.id).all()
    return render_template("urls.html", urls=urls)


@url_bp.route("/qrcode/<short_code>")
@limiter.limit("60 per minute")
def serve_qrcode(short_code):
    URL.query.filter_by(short_code=short_code).first_or_404()
    url_curta_completa = request.host_url + short_code

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url_curta_completa)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    byte_io = BytesIO()
    img.save(byte_io, format="PNG")
    byte_io.seek(0)

    return send_file(byte_io, mimetype="image/png", as_attachment=False, download_name=f"qrcode_{short_code}.png")


@url_bp.route("/<codigo_curto>")
def redirecionar_url(codigo_curto):
    url_entry = URL.query.filter_by(short_code=codigo_curto).first_or_404()
    registrar_clique(url_entry)
    return redirect(url_entry.original_url)
