from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from flask_login import current_user

from encurtarjr.forms import ShortenURLForm
from encurtarjr.extensions import limiter
from encurtarjr.services.url_service import criar_url_encurtada


main_bp = Blueprint("main", __name__)


@main_bp.route("/", methods=["GET", "POST"])
@limiter.limit("10 per minute", methods=["POST"])
def index():
    form = ShortenURLForm()

    if form.validate_on_submit():
        if not current_user.is_authenticated:
            links_anonimos = session.get("anon_links", [])
            if len(links_anonimos) >= 20:
                flash("Você atingiu o limite gratuito de 20 links! Crie uma conta para continuar.", "danger")
                return redirect(url_for("auth.register"))

        usuario_atual = current_user if current_user.is_authenticated else None
        resultado = criar_url_encurtada(
            form.url.data,
            form.custom_url.data,
            user_id=usuario_atual.id if usuario_atual else None,
        )

        if not resultado.success:
            flash(resultado.message, "danger")
            return render_template("index.html", form=form)

        if not current_user.is_authenticated:
            links_anonimos = session.get("anon_links", [])
            links_anonimos.append(resultado.short_code)
            session["anon_links"] = links_anonimos

        url_curta_completa = request.host_url + resultado.short_code
        return render_template("index.html", form=form, url_curta=url_curta_completa, code=resultado.short_code)

    if request.method == "POST":
        flash("Informe uma URL válida para encurtar.", "danger")

    return render_template("index.html", form=form)
