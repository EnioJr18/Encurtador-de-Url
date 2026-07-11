from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user
from sqlalchemy import func, or_

from encurtarjr.decorators import admin_required
from encurtarjr.extensions import bcrypt, db
from encurtarjr.models import URL, User
from encurtarjr.services.url_service import criar_url_encurtada
from encurtarjr.utils import normalizar_codigo_personalizado, validar_codigo_personalizado, validar_url_original


admin_bp = Blueprint("admin", __name__, url_prefix="/admin")
ADMIN_PER_PAGE = 10


def user_metrics_query():
    return db.session.query(User.id, User.username, User.is_admin, func.count(URL.id).label("link_count"), func.coalesce(func.sum(URL.click_count), 0).label("total_clicks")).outerjoin(URL, URL.user_id == User.id).group_by(User.id, User.username, User.is_admin)


def current_page():
    try:
        page = int(request.args.get("page", 1))
    except (TypeError, ValueError):
        return 1
    return max(page, 1)


def pagination_args():
    return {key: value for key, value in request.args.items() if key != "page" and value}


def user_choices():
    return User.query.order_by(User.username.asc()).all()


def parse_owner_id():
    value = request.form.get("user_id", "").strip()
    if not value:
        return None, None
    user = db.session.get(User, int(value)) if value.isdigit() else None
    return (user.id, None) if user else (None, "Usuario selecionado nao existe.")


@admin_bp.route("/")
@admin_required
def dashboard():
    stats = {"total_users": User.query.count(), "total_links": URL.query.count(), "total_clicks": db.session.query(func.coalesce(func.sum(URL.click_count), 0)).scalar() or 0, "links_without_clicks": URL.query.filter(func.coalesce(URL.click_count, 0) == 0).count()}
    most_clicked = URL.query.order_by(URL.click_count.desc(), URL.id.asc()).first()
    stats["most_clicked"] = most_clicked if most_clicked and most_clicked.click_count else None
    top_users = user_metrics_query().order_by(func.count(URL.id).desc(), func.sum(URL.click_count).desc(), User.username.asc()).limit(5).all()
    top_links = URL.query.order_by(URL.click_count.desc(), URL.id.asc()).limit(5).all()
    return render_template("admin/dashboard.html", stats=stats, top_users=top_users, top_links=top_links)


@admin_bp.route("/users")
@admin_required
def users():
    query_text = request.args.get("q", "").strip()
    role_filter = request.args.get("role", "all").strip().lower()
    query = user_metrics_query()
    if query_text:
        query = query.filter(User.username.ilike(f"%{query_text}%"))
    if role_filter == "admins":
        query = query.filter(User.is_admin.is_(True))
    elif role_filter == "users":
        query = query.filter(User.is_admin.is_(False))
    else:
        role_filter = "all"
    pagination = query.order_by(User.username.asc()).paginate(page=current_page(), per_page=ADMIN_PER_PAGE, error_out=False)
    return render_template("admin/users.html", users=pagination.items, pagination=pagination, pagination_args=pagination_args(), filters={"q": query_text, "role": role_filter})


@admin_bp.route("/users/new", methods=["GET", "POST"])
@admin_required
def user_create():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        if not username or not password:
            flash("Informe usuario e senha para criar a conta.", "danger")
        elif len(username) > 150 or len(password) > 200:
            flash("Usuario ou senha excede o tamanho permitido.", "danger")
        elif User.query.filter_by(username=username).first():
            flash("Nome de usuario ja existe.", "danger")
        else:
            user = User(username=username, password=bcrypt.generate_password_hash(password).decode("utf-8"), is_admin="is_admin" in request.form)
            db.session.add(user)
            db.session.commit()
            flash("Usuario criado com sucesso.", "success")
            return redirect(url_for("admin.users"))
    return render_template("admin/user_form.html", user=None)


@admin_bp.route("/users/<int:user_id>/edit", methods=["GET", "POST"])
@admin_required
def user_edit(user_id):
    user = db.get_or_404(User, user_id)
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        duplicate = User.query.filter(User.username == username, User.id != user.id).first()
        if not username or len(username) > 150 or duplicate:
            flash("Informe um nome de usuario unico.", "danger")
        elif request.form.get("password") and len(request.form["password"]) > 200:
            flash("A senha excede o tamanho permitido.", "danger")
        elif user.id == current_user.id and "is_admin" not in request.form:
            flash("Nao e permitido remover seu proprio acesso administrativo.", "danger")
        else:
            user.username = username
            user.is_admin = "is_admin" in request.form
            if request.form.get("password"):
                user.password = bcrypt.generate_password_hash(request.form["password"]).decode("utf-8")
            db.session.commit()
            flash("Usuario atualizado com sucesso.", "success")
            return redirect(url_for("admin.users"))
    return render_template("admin/user_form.html", user=user)


@admin_bp.post("/users/<int:user_id>/delete")
@admin_required
def user_delete(user_id):
    user = db.get_or_404(User, user_id)
    if user.id == current_user.id:
        flash("Nao e permitido excluir sua propria conta administrativa.", "danger")
    else:
        URL.query.filter_by(user_id=user.id).update({URL.user_id: None})
        db.session.delete(user)
        db.session.commit()
        flash("Usuario removido; seus links foram mantidos sem dono.", "success")
    return redirect(url_for("admin.users"))


@admin_bp.route("/links")
@admin_required
def links():
    query_text = request.args.get("q", "").strip()
    clicks_filter = request.args.get("clicks", "all").strip().lower()
    query = URL.query.outerjoin(User)
    if query_text:
        search = f"%{query_text}%"
        query = query.filter(or_(URL.short_code.ilike(search), URL.original_url.ilike(search), User.username.ilike(search)))
    if clicks_filter == "clicked":
        query = query.filter(func.coalesce(URL.click_count, 0) > 0)
    elif clicks_filter == "unclicked":
        query = query.filter(func.coalesce(URL.click_count, 0) == 0)
    else:
        clicks_filter = "all"
    pagination = query.order_by(URL.click_count.desc(), URL.id.desc()).paginate(page=current_page(), per_page=ADMIN_PER_PAGE, error_out=False)
    return render_template("admin/links.html", links=pagination.items, pagination=pagination, pagination_args=pagination_args(), filters={"q": query_text, "clicks": clicks_filter})


@admin_bp.route("/links/new", methods=["GET", "POST"])
@admin_required
def link_create():
    if request.method == "POST":
        owner_id, owner_error = parse_owner_id()
        if owner_error:
            flash(owner_error, "danger")
        else:
            result = criar_url_encurtada(request.form.get("original_url"), request.form.get("short_code"), user_id=owner_id)
            if result.success:
                flash("Link criado com sucesso.", "success")
                return redirect(url_for("admin.links"))
            flash(result.message, "danger")
    return render_template("admin/link_form.html", link=None, users=user_choices())


@admin_bp.route("/links/<int:link_id>/edit", methods=["GET", "POST"])
@admin_required
def link_edit(link_id):
    link = db.get_or_404(URL, link_id)
    if request.method == "POST":
        original_url, url_error = validar_url_original(request.form.get("original_url"))
        short_code = normalizar_codigo_personalizado(request.form.get("short_code"))
        code_error = validar_codigo_personalizado(short_code) or ("Informe um codigo curto." if short_code is None else None)
        owner_id, owner_error = parse_owner_id()
        duplicate = URL.query.filter(URL.short_code == short_code, URL.id != link.id).first() if short_code else None
        if url_error or code_error or owner_error or duplicate:
            flash(url_error or code_error or owner_error or "Codigo curto ja esta em uso.", "danger")
        else:
            link.original_url, link.short_code, link.user_id = original_url, short_code, owner_id
            db.session.commit()
            flash("Link atualizado com sucesso.", "success")
            return redirect(url_for("admin.links"))
    return render_template("admin/link_form.html", link=link, users=user_choices())


@admin_bp.post("/links/<int:link_id>/delete")
@admin_required
def link_delete(link_id):
    link = db.get_or_404(URL, link_id)
    db.session.delete(link)
    db.session.commit()
    flash("Link removido com sucesso.", "success")
    return redirect(url_for("admin.links"))
