from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from flask_login import current_user

from encurtarjr.services.url_service import criar_url_encurtada


main_bp = Blueprint("main", __name__)


@main_bp.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if not current_user.is_authenticated:
            links_anonimos = session.get("anon_links", [])
            if len(links_anonimos) >= 20:
                flash("Você atingiu o limite gratuito de 20 links! Crie uma conta para continuar.", "danger")
                return redirect(url_for("auth.register"))

        usuario_atual = current_user if current_user.is_authenticated else None
        resultado = criar_url_encurtada(
            request.form.get("url"),
            request.form.get("custom_url"),
            user_id=usuario_atual.id if usuario_atual else None,
        )

        if not resultado.success:
            flash(resultado.message, "danger")
            return render_template("index.html")

        if not current_user.is_authenticated:
            links_anonimos = session.get("anon_links", [])
            links_anonimos.append(resultado.short_code)
            session["anon_links"] = links_anonimos

        url_curta_completa = request.host_url + resultado.short_code
        return render_template("index.html", url_curta=url_curta_completa, code=resultado.short_code)

    return render_template("index.html")


@main_bp.app_errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404
