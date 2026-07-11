from flask import abort

from encurtarjr.extensions import db
from encurtarjr import create_app
from encurtarjr.models import URL, User


def register(client, username="usuario", password="123456"):
    return client.post("/register", data={"username": username, "password": password})


def login(client, username="usuario", password="123456"):
    return client.post("/login", data={"username": username, "password": password})


def create_logged_user(client, username="usuario", password="123456"):
    register(client, username, password)
    return login(client, username, password)


def make_admin(username="admin"):
    user = User.query.filter_by(username=username).first()
    user.is_admin = True
    db.session.commit()
    return user


def shorten(client, url="https://example.com", custom_url="meulink"):
    return client.post("/", data={"url": url, "custom_url": custom_url})


def test_home_returns_200(client):
    response = client.get("/")
    assert response.status_code == 200


def test_auth_pages_render_password_toggle_controls(client):
    login_page = client.get("/login")
    register_page = client.get("/register")

    assert login_page.status_code == 200
    assert register_page.status_code == 200
    assert b'data-password-toggle="password"' in login_page.data
    assert b'data-password-toggle="password"' in register_page.data


def test_valid_register_redirects(client):
    response = register(client)
    assert response.status_code == 302
    assert User.query.filter_by(username="usuario").first() is not None


def test_duplicate_register_fails_without_500(client):
    register(client)
    response = register(client)
    assert response.status_code == 200
    assert User.query.filter_by(username="usuario").count() == 1


def test_register_missing_fields_does_not_break(client):
    response = client.post("/register", data={})
    assert response.status_code == 200


def test_valid_login_redirects(client):
    register(client)
    response = login(client)
    assert response.status_code == 302


def test_wrong_password_does_not_authenticate(client):
    register(client)
    response = login(client, password="senha-errada")
    assert response.status_code == 200

    protected = client.get("/urls")
    assert protected.status_code == 302
    assert "/login" in protected.headers["Location"]


def test_missing_user_login_does_not_authenticate(client):
    response = login(client, username="naoexiste")
    assert response.status_code == 200

    protected = client.get("/urls")
    assert protected.status_code == 302
    assert "/login" in protected.headers["Location"]


def test_valid_url_creates_short_link(client):
    response = shorten(client, custom_url="valido")
    assert response.status_code == 200
    assert URL.query.filter_by(short_code="valido").first() is not None
    assert b"data-copy-link" in response.data
    assert b'aria-live="polite"' in response.data
    assert b"qrCodeModal" in response.data


def test_url_without_http_or_https_is_rejected(client):
    response = shorten(client, url="example.com", custom_url="semhttp")
    assert response.status_code == 200
    assert URL.query.filter_by(short_code="semhttp").first() is None


def test_javascript_url_is_rejected(client):
    response = shorten(client, url="javascript:alert(1)", custom_url="script")
    assert response.status_code == 200
    assert URL.query.filter_by(short_code="script").first() is None


def test_custom_url_with_space_is_rejected(client):
    response = shorten(client, custom_url="meu link")
    assert response.status_code == 200
    assert URL.query.count() == 0


def test_custom_url_with_slash_is_rejected(client):
    response = shorten(client, custom_url="meu/link")
    assert response.status_code == 200
    assert URL.query.count() == 0


def test_reserved_custom_url_is_rejected(client):
    response = shorten(client, custom_url="login")
    assert response.status_code == 200
    assert URL.query.count() == 0


def test_duplicate_custom_url_is_rejected(client):
    shorten(client, custom_url="duplicado")
    response = shorten(client, url="https://example.org", custom_url="duplicado")
    assert response.status_code == 200
    assert URL.query.filter_by(short_code="duplicado").count() == 1


def test_urls_without_login_redirects_to_login(client):
    response = client.get("/urls")
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_admin_requires_login(client):
    response = client.get("/admin/")
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_common_user_cannot_access_admin(client):
    create_logged_user(client)
    response = client.get("/admin/")
    assert response.status_code == 403
    assert b"Acesso restrito" in response.data


def test_admin_can_access_admin_pages_and_navbar(client):
    register(client, username="admin")
    make_admin()
    login(client, username="admin")

    assert client.get("/admin/").status_code == 200
    assert client.get("/admin/users").status_code == 200
    assert client.get("/admin/links").status_code == 200
    assert b"Admin" in client.get("/").data


def test_admin_promote_command(runner, client):
    register(client, username="promover")
    result = runner.invoke(args=["admin", "promote", "promover"])
    assert result.exit_code == 0
    assert User.query.filter_by(username="promover").first().is_admin is True

    missing = runner.invoke(args=["admin", "promote", "inexistente"])
    assert missing.exit_code != 0
    assert "Usuario nao encontrado" in missing.output


def test_common_user_cannot_post_admin_crud(client):
    create_logged_user(client)
    responses = [
        client.post("/admin/users/new", data={"username": "outro", "password": "123456"}),
        client.post("/admin/links/new", data={"original_url": "https://example.com", "short_code": "bloqueado"}),
    ]
    assert all(response.status_code == 403 for response in responses)


def test_admin_user_crud_preserves_links_and_hides_password(client):
    register(client, username="admin")
    make_admin()
    login(client, username="admin")
    assert client.post("/admin/users/new", data={"username": "alvo", "password": "senha-secreta"}).status_code == 302
    alvo = User.query.filter_by(username="alvo").first()
    original_hash = alvo.password
    response = client.post(f"/admin/users/{alvo.id}/edit", data={"username": "editado", "password": "", "is_admin": "on"})
    assert response.status_code == 302
    assert db.session.get(User, alvo.id).username == "editado"
    assert original_hash.encode() not in client.get("/admin/users").data
    URL.query.filter_by(short_code="vinculado").delete()
    db.session.add(URL(original_url="https://example.com", short_code="vinculado", user_id=alvo.id))
    db.session.commit()
    assert client.post(f"/admin/users/{alvo.id}/delete").status_code == 302
    assert URL.query.filter_by(short_code="vinculado").first().user_id is None


def test_admin_link_crud_uses_public_validations(client):
    register(client, username="admin")
    make_admin()
    login(client, username="admin")
    assert client.post("/admin/links/new", data={"original_url": "https://example.com", "short_code": "admin-link"}).status_code == 302
    link = URL.query.filter_by(short_code="admin-link").first()
    assert client.post("/admin/links/new", data={"original_url": "javascript:alert(1)", "short_code": "invalido"}).status_code == 200
    assert client.post("/admin/links/new", data={"original_url": "https://example.com", "short_code": "admin"}).status_code == 200
    assert client.post(f"/admin/links/{link.id}/edit", data={"original_url": "https://example.org", "short_code": "editado"}).status_code == 302
    assert db.session.get(URL, link.id).short_code == "editado"
    assert client.post(f"/admin/links/{link.id}/delete").status_code == 302
    assert db.session.get(URL, link.id) is None


def test_admin_users_list_renders_pagination_and_filters_username(client):
    register(client, username="admin")
    make_admin()
    for index in range(12):
        db.session.add(User(username=f"usuario-{index}", password="hash"))
    db.session.commit()
    login(client, username="admin")

    page = client.get("/admin/users")
    search = client.get("/admin/users?q=usuario-11")

    assert page.status_code == 200
    assert b"Paginacao administrativa" in page.data
    assert b"usuario-11" in search.data
    assert b"usuario-10" not in search.data


def test_admin_users_filter_admins_and_invalid_page(client):
    register(client, username="admin")
    make_admin()
    db.session.add(User(username="comum", password="hash", is_admin=False))
    db.session.add(User(username="outro-admin", password="hash", is_admin=True))
    db.session.commit()
    login(client, username="admin")

    admins = client.get("/admin/users?role=admins")
    invalid_page = client.get("/admin/users?page=abc")

    assert admins.status_code == 200
    assert b"outro-admin" in admins.data
    assert b"comum" not in admins.data
    assert invalid_page.status_code == 200


def test_admin_links_list_renders_pagination_and_filters_short_code(client):
    register(client, username="admin")
    admin = make_admin()
    for index in range(12):
        db.session.add(URL(original_url=f"https://example.com/{index}", short_code=f"link-{index}", user_id=admin.id))
    db.session.commit()
    login(client, username="admin")

    page = client.get("/admin/links")
    search = client.get("/admin/links?q=link-11")

    assert page.status_code == 200
    assert b"Paginacao administrativa" in page.data
    assert b"link-11" in search.data
    assert b"link-10" not in search.data


def test_admin_links_filter_without_clicks_and_invalid_page(client):
    register(client, username="admin")
    make_admin()
    db.session.add(URL(original_url="https://example.com/clicked", short_code="com-clique", click_count=3))
    db.session.add(URL(original_url="https://example.com/unclicked", short_code="sem-clique", click_count=0))
    db.session.commit()
    login(client, username="admin")

    unclicked = client.get("/admin/links?clicks=unclicked")
    invalid_page = client.get("/admin/links?page=-9")

    assert unclicked.status_code == 200
    assert b"sem-clique" in unclicked.data
    assert b"com-clique" not in unclicked.data
    assert invalid_page.status_code == 200


def test_common_user_cannot_access_admin_filters(client):
    create_logged_user(client)

    responses = [
        client.get("/admin/users?q=usuario&role=admins"),
        client.get("/admin/links?q=link&clicks=unclicked"),
    ]

    assert all(response.status_code == 403 for response in responses)


def test_urls_with_login_returns_200(client):
    create_logged_user(client)
    response = client.get("/urls")
    assert response.status_code == 200
    assert b"Nenhum link criado ainda" in response.data
    assert b"Links criados" in response.data
    assert b"Total de acessos" in response.data


def test_urls_with_links_render_dashboard_components(client):
    create_logged_user(client)
    shorten(client, custom_url="mais-acessado")
    shorten(client, url="https://example.org", custom_url="sem-acessos")
    most_clicked = URL.query.filter_by(short_code="mais-acessado").first()
    most_clicked.click_count = 4
    db.session.commit()

    response = client.get("/urls")

    assert response.status_code == 200
    assert b"mais-acessado" in response.data
    assert b"QR Code" in response.data
    assert b"data-copy-link" in response.data
    assert b"data-qr-url" in response.data
    assert b"qrCodeModal" in response.data
    assert b"Links criados" in response.data
    assert b"Total de acessos" in response.data
    assert b"Mais acessado" in response.data
    assert b"Sem acessos ainda" in response.data
    assert b"4 acessos" in response.data


def test_urls_with_many_links_render_pagination(client):
    create_logged_user(client)
    user = User.query.filter_by(username="usuario").first()
    for index in range(12):
        db.session.add(URL(original_url=f"https://example.com/{index}", short_code=f"meu-link-{index}", user_id=user.id))
    db.session.commit()

    response = client.get("/urls")

    assert response.status_code == 200
    assert b"Paginacao dos links" in response.data
    assert b"data-copy-link" in response.data
    assert b"qrCodeModal" in response.data


def test_urls_search_by_short_code_and_original_url(client):
    create_logged_user(client)
    user = User.query.filter_by(username="usuario").first()
    db.session.add(URL(original_url="https://github.com/enio/projeto", short_code="github-projeto", user_id=user.id))
    db.session.add(URL(original_url="https://example.com/docs", short_code="documentacao", user_id=user.id))
    db.session.commit()

    by_code = client.get("/urls?q=github-projeto")
    by_url = client.get("/urls?q=docs")

    assert by_code.status_code == 200
    assert b"github-projeto" in by_code.data
    assert b"documentacao" not in by_code.data
    assert b"documentacao" in by_url.data


def test_urls_click_filters(client):
    create_logged_user(client)
    user = User.query.filter_by(username="usuario").first()
    db.session.add(URL(original_url="https://example.com/clicked", short_code="clicado", click_count=5, user_id=user.id))
    db.session.add(URL(original_url="https://example.com/unclicked", short_code="sem-acesso", click_count=0, user_id=user.id))
    db.session.commit()

    clicked = client.get("/urls?clicks=clicked")
    unclicked = client.get("/urls?clicks=unclicked")

    clicked_table = clicked.data.split(b"<tbody>", 1)[1].split(b"</tbody>", 1)[0]
    unclicked_table = unclicked.data.split(b"<tbody>", 1)[1].split(b"</tbody>", 1)[0]
    assert b"clicado" in clicked_table
    assert b"sem-acesso" not in clicked_table
    assert b"sem-acesso" in unclicked_table
    assert b"clicado" not in unclicked_table


def test_urls_sort_by_most_clicked_and_invalid_page(client):
    create_logged_user(client)
    user = User.query.filter_by(username="usuario").first()
    db.session.add(URL(original_url="https://example.com/low", short_code="baixo", click_count=1, user_id=user.id))
    db.session.add(URL(original_url="https://example.com/high", short_code="alto", click_count=9, user_id=user.id))
    db.session.commit()

    sorted_response = client.get("/urls?sort=clicks_desc")
    invalid_page = client.get("/urls?page=valor-invalido")
    table = sorted_response.data.split(b"<tbody>", 1)[1].split(b"</tbody>", 1)[0]

    assert sorted_response.status_code == 200
    assert table.index(b"alto") < table.index(b"baixo")
    assert invalid_page.status_code == 200


def test_urls_are_scoped_to_current_user(client):
    create_logged_user(client)
    owner = User.query.filter_by(username="usuario").first()
    db.session.add(URL(original_url="https://example.com/own", short_code="meu-privado", user_id=owner.id))
    db.session.commit()
    client.get("/logout")

    register(client, username="outro")
    other = User.query.filter_by(username="outro").first()
    db.session.add(URL(original_url="https://example.com/other", short_code="outro-privado", user_id=other.id))
    db.session.commit()
    login(client, username="outro")

    response = client.get("/urls?q=privado")

    assert response.status_code == 200
    assert b"outro-privado" in response.data
    assert b"meu-privado" not in response.data


def test_qrcode_route_returns_png(client):
    shorten(client, custom_url="imagem-qr")

    response = client.get("/qrcode/imagem-qr")

    assert response.status_code == 200
    assert response.mimetype == "image/png"


def test_existing_short_code_redirects(client):
    shorten(client, custom_url="destino")
    response = client.get("/destino")
    assert response.status_code == 302
    assert response.headers["Location"] == "https://example.com"

    db.session.expire_all()
    assert URL.query.filter_by(short_code="destino").first().click_count == 1


def test_missing_short_code_returns_404(client):
    response = client.get("/naoexiste")
    assert response.status_code == 404
    assert b"Pagina nao encontrada" in response.data


def test_missing_route_returns_404(client):
    response = client.get("/rota/sem/correspondencia")
    assert response.status_code == 404
    assert b"Voltar ao inicio" in response.data


def test_invalid_inputs_do_not_return_500(client):
    responses = [
        client.post("/", data={}),
        client.post("/", data={"url": "ftp://example.com", "custom_url": "ftp"}),
        client.post("/", data={"url": "https://example.com", "custom_url": "com espaço"}),
        client.post("/login", data={}),
        client.post("/register", data={}),
    ]

    assert all(response.status_code < 500 for response in responses)


def test_csrf_is_enabled_outside_testing():
    class CSRFEnabledConfig:
        TESTING = False
        SECRET_KEY = "csrf-test-secret"
        SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
        SQLALCHEMY_TRACK_MODIFICATIONS = False
        WTF_CSRF_ENABLED = True
        SESSION_COOKIE_SECURE = False
        SESSION_COOKIE_HTTPONLY = True
        SESSION_COOKIE_SAMESITE = "Lax"

    app = create_app(CSRFEnabledConfig)

    with app.app_context():
        db.create_all()
        response = app.test_client().post("/login", data={"username": "usuario", "password": "123456"})
        db.session.remove()
        db.drop_all()

    assert response.status_code == 400
    assert b"Sua sessao expirou" in response.data


def test_rate_limit_is_disabled_in_testing(app):
    assert app.config["RATELIMIT_ENABLED"] is False


def test_rate_limit_returns_friendly_response_outside_testing():
    class RateLimitConfig:
        TESTING = False
        SECRET_KEY = "rate-limit-test-secret"
        SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
        SQLALCHEMY_TRACK_MODIFICATIONS = False
        WTF_CSRF_ENABLED = False
        RATELIMIT_ENABLED = True
        RATELIMIT_STORAGE_URI = "memory://"
        RATELIMIT_HEADERS_ENABLED = True
        SESSION_COOKIE_SECURE = False
        SESSION_COOKIE_HTTPONLY = True
        SESSION_COOKIE_SAMESITE = "Lax"

    app = create_app(RateLimitConfig)

    with app.app_context():
        db.create_all()
        client = app.test_client()
        responses = [
            client.post("/login", data={"username": "usuario", "password": "123456"})
            for _ in range(6)
        ]
        db.session.remove()
        db.drop_all()

    assert responses[-1].status_code == 429
    assert b"Muitas tentativas" in responses[-1].data


def test_bad_request_and_internal_error_render_friendly_pages():
    class ErrorHandlerConfig:
        TESTING = False
        PROPAGATE_EXCEPTIONS = False
        SECRET_KEY = "error-handler-test-secret"
        SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
        SQLALCHEMY_TRACK_MODIFICATIONS = False
        WTF_CSRF_ENABLED = False
        RATELIMIT_ENABLED = False
        SESSION_COOKIE_SECURE = False
        SESSION_COOKIE_HTTPONLY = True
        SESSION_COOKIE_SAMESITE = "Lax"
        LOG_LEVEL = "CRITICAL"

    app = create_app(ErrorHandlerConfig)

    @app.get("/test-bad-request")
    def trigger_bad_request():
        abort(400)

    @app.get("/test-internal-error")
    def trigger_internal_error():
        raise RuntimeError("intentional test error")

    client = app.test_client()
    bad_request = client.get("/test-bad-request")
    internal_error = client.get("/test-internal-error")

    assert bad_request.status_code == 400
    assert b"Requisicao invalida" in bad_request.data
    assert internal_error.status_code == 500
    assert b"Algo deu errado" in internal_error.data
