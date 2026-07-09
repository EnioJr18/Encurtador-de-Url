from io import BytesIO

import qrcode  # type: ignore
from flask import Blueprint, flash, redirect, render_template, request, send_file, session, url_for  # type: ignore
from flask_login import current_user, login_required, login_user, logout_user  # type: ignore
from sqlalchemy.exc import IntegrityError, SQLAlchemyError  # type: ignore

from models import URL, User, db
from utils import (
    gerar_codigo_curto,
    normalizar_codigo_personalizado,
    slug_reservado,
    validar_codigo_personalizado,
    validar_url_original,
)


main = Blueprint("main", __name__)
MAX_AUTO_CODE_ATTEMPTS = 10


def gerar_codigo_unico():
    for _ in range(MAX_AUTO_CODE_ATTEMPTS):
        codigo = gerar_codigo_curto()
        if slug_reservado(codigo):
            continue
        if not URL.query.filter_by(short_code=codigo).first():
            return codigo

    return None


@main.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if not current_user.is_authenticated:
            links_anonimos = session.get("anon_links", [])

            if len(links_anonimos) >= 20:
                flash("Você atingiu o limite gratuito de 20 links! Crie uma conta para continuar.", "danger")
                return redirect(url_for("main.register"))

        usuario_atual = current_user if current_user.is_authenticated else None
        url_original, erro_url = validar_url_original(request.form.get("url"))

        if erro_url:
            flash(erro_url, "danger")
            return render_template("index.html")

        codigo_curto = normalizar_codigo_personalizado(request.form.get("custom_url"))
        erro_codigo = validar_codigo_personalizado(codigo_curto)

        if erro_codigo:
            flash(erro_codigo, "danger")
            return render_template("index.html")

        codigo_personalizado_informado = codigo_curto is not None

        if codigo_curto:
            existente = URL.query.filter_by(short_code=codigo_curto).first()
            if existente:
                flash("O código curto personalizado já está em uso. Tente outro.", "danger")
                return render_template("index.html")
        else:
            codigo_curto = gerar_codigo_unico()
            if not codigo_curto:
                flash("Não foi possível gerar um código curto agora. Tente novamente.", "danger")
                return render_template("index.html")

        nova_url = URL(
            original_url=url_original,
            short_code=codigo_curto,
            user_id=usuario_atual.id if usuario_atual else None,
        )

        try:
            db.session.add(nova_url)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            if codigo_personalizado_informado:
                flash("Este código curto já está em uso. Escolha outro.", "danger")
            else:
                flash("Não foi possível salvar o link por colisão de código. Tente novamente.", "danger")
            return render_template("index.html")
        except SQLAlchemyError:
            db.session.rollback()
            flash("Erro inesperado ao salvar o link. Tente novamente.", "danger")
            return render_template("index.html")

        if not current_user.is_authenticated:
            links_anonimos = session.get("anon_links", [])
            links_anonimos.append(codigo_curto)
            session["anon_links"] = links_anonimos

        url_curta_completa = request.host_url + codigo_curto
        return render_template("index.html", url_curta=url_curta_completa, code=codigo_curto)

    return render_template("index.html")


@main.route("/<codigo_curto>")
def redirecionar_url(codigo_curto):
    url_entry = URL.query.filter_by(short_code=codigo_curto).first_or_404()

    URL.query.filter_by(id=url_entry.id).update({
        URL.click_count: URL.click_count + 1,
        URL.acesso_data: db.func.now(),
    })
    db.session.commit()

    return redirect(url_entry.original_url)


@main.route("/urls")
@login_required
def listar_urls():
    urls = URL.query.filter_by(user_id=current_user.id).all()
    return render_template("urls.html", urls=urls)


@main.route("/qrcode/<short_code>")
def serve_qrcode(short_code):
    url_entry = URL.query.filter_by(short_code=short_code).first_or_404()
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


@main.app_errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


@main.route("/register", methods=["GET", "POST"])
def register():
    from app import bcrypt

    if current_user.is_authenticated:
        flash("Você já está logado.", "info")
        return redirect(url_for("main.index"))

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("Nome de usuário já existe. Escolha outro.", "danger")
            return render_template("register.html")

        senha_hash = bcrypt.generate_password_hash(password).decode("utf-8")
        new_user = User(username=username, password=senha_hash)
        db.session.add(new_user)
        db.session.commit()

        flash("Conta criada com sucesso! Faça login.", "success")
        return redirect(url_for("main.login"))

    return render_template("register.html")


@main.route("/login", methods=["GET", "POST"])
def login():
    from app import bcrypt

    if current_user.is_authenticated:
        flash("Você já está logado.", "info")
        return redirect(url_for("main.index"))

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            flash("Login realizado com sucesso!", "success")
            return redirect(url_for("main.index"))

        flash("Falha no login. Verifique suas credenciais.", "danger")
        return render_template("login.html")

    return render_template("login.html")


@main.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Você saiu da sua conta.", "info")
    return redirect(url_for("main.login"))
