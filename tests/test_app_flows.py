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


def test_urls_with_login_returns_200(client):
    create_logged_user(client)
    response = client.get("/urls")
    assert response.status_code == 200


def test_urls_with_links_render_dashboard_components(client):
    create_logged_user(client)
    shorten(client, custom_url="painel")

    response = client.get("/urls")

    assert response.status_code == 200
    assert b"painel" in response.data
    assert b"QR Code" in response.data
    assert b"data-copy-link" in response.data
    assert b"data-qr-url" in response.data
    assert b"qrCodeModal" in response.data


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
