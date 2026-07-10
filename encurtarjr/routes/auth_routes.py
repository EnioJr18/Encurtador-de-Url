from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import current_user, login_required, login_user, logout_user

from encurtarjr.extensions import bcrypt, db, limiter
from encurtarjr.forms import LoginForm, RegisterForm
from encurtarjr.models import User


auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["GET", "POST"])
@limiter.limit("5 per hour", methods=["POST"])
def register():
    form = RegisterForm()

    if current_user.is_authenticated:
        flash("Você já está logado.", "info")
        return redirect(url_for("main.index"))

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("Nome de usuário já existe. Escolha outro.", "danger")
            return render_template("register.html", form=form)

        senha_hash = bcrypt.generate_password_hash(password).decode("utf-8")
        new_user = User(username=username, password=senha_hash)
        db.session.add(new_user)
        db.session.commit()

        flash("Conta criada com sucesso! Faça login.", "success")
        return redirect(url_for("auth.login"))

    if form.is_submitted():
        flash("Informe usuário e senha para criar a conta.", "danger")

    return render_template("register.html", form=form)


@auth_bp.route("/login", methods=["GET", "POST"])
@limiter.limit("5 per minute", methods=["POST"])
def login():
    form = LoginForm()

    if current_user.is_authenticated:
        flash("Você já está logado.", "info")
        return redirect(url_for("main.index"))

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            flash("Login realizado com sucesso!", "success")
            return redirect(url_for("main.index"))

        flash("Falha no login. Verifique suas credenciais.", "danger")
        return render_template("login.html", form=form)

    if form.is_submitted():
        flash("Falha no login. Verifique suas credenciais.", "danger")

    return render_template("login.html", form=form)


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Você saiu da sua conta.", "info")
    return redirect(url_for("auth.login"))
