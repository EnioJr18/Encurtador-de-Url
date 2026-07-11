from io import BytesIO

import qrcode
from flask import Blueprint, redirect, render_template, request, send_file
from flask_login import current_user, login_required
from sqlalchemy import func, or_

from encurtarjr.extensions import limiter
from encurtarjr.models import URL
from encurtarjr.services.url_service import registrar_clique


url_bp = Blueprint("urls", __name__)
URLS_PER_PAGE = 10


def current_page():
    try:
        page = int(request.args.get("page", 1))
    except (TypeError, ValueError):
        return 1
    return max(page, 1)


def pagination_args():
    return {key: value for key, value in request.args.items() if key != "page" and value}


def apply_url_sorting(query, sort_option):
    sort_options = {
        "recent": URL.id.desc(),
        "oldest": URL.id.asc(),
        "clicks_desc": URL.click_count.desc(),
        "clicks_asc": URL.click_count.asc(),
        "short_code": URL.short_code.asc(),
    }
    return query.order_by(sort_options.get(sort_option, URL.id.desc()), URL.id.desc())


def user_link_stats(user_id):
    base_query = URL.query.filter_by(user_id=user_id)
    total_links = base_query.count()
    total_clicks = base_query.with_entities(func.coalesce(func.sum(URL.click_count), 0)).scalar() or 0
    most_clicked = base_query.order_by(URL.click_count.desc(), URL.id.desc()).first()
    return {
        "total_links": total_links,
        "total_clicks": total_clicks,
        "links_without_clicks": base_query.filter(func.coalesce(URL.click_count, 0) == 0).count(),
        "most_clicked": most_clicked if total_clicks else None,
        "max_clicks": (most_clicked.click_count or 0) if most_clicked else 0,
    }


@url_bp.route("/urls")
@login_required
def listar_urls():
    query_text = request.args.get("q", "").strip()
    sort_option = request.args.get("sort", "recent").strip().lower()
    clicks_filter = request.args.get("clicks", "all").strip().lower()
    valid_sorts = {"recent", "oldest", "clicks_desc", "clicks_asc", "short_code"}
    if sort_option not in valid_sorts:
        sort_option = "recent"

    query = URL.query.filter_by(user_id=current_user.id)
    if query_text:
        search = f"%{query_text}%"
        query = query.filter(or_(URL.short_code.ilike(search), URL.original_url.ilike(search)))
    if clicks_filter == "clicked":
        query = query.filter(func.coalesce(URL.click_count, 0) > 0)
    elif clicks_filter == "unclicked":
        query = query.filter(func.coalesce(URL.click_count, 0) == 0)
    else:
        clicks_filter = "all"

    pagination = apply_url_sorting(query, sort_option).paginate(page=current_page(), per_page=URLS_PER_PAGE, error_out=False)

    return render_template(
        "urls.html",
        urls=pagination.items,
        stats=user_link_stats(current_user.id),
        pagination=pagination,
        pagination_args=pagination_args(),
        pagination_label="Paginacao dos links",
        filters={"q": query_text, "sort": sort_option, "clicks": clicks_filter},
    )


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
