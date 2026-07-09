import re
import secrets
import string
from urllib.parse import urlparse


MAX_ORIGINAL_URL_LENGTH = 500
MIN_CUSTOM_CODE_LENGTH = 3
MAX_CUSTOM_CODE_LENGTH = 50
CUSTOM_CODE_PATTERN = re.compile(r"^[a-z0-9_-]+$")
RESERVED_SLUGS = {
    "admin",
    "api",
    "assets",
    "dashboard",
    "favicon.ico",
    "login",
    "logout",
    "qrcode",
    "register",
    "static",
    "stats",
    "urls",
}


def gerar_codigo_curto(tamanho=6):
    caracteres = string.ascii_lowercase + string.digits
    return "".join(secrets.choice(caracteres) for _ in range(tamanho))


def validar_url_original(url):
    url_normalizada = (url or "").strip()

    if not url_normalizada:
        return None, "Informe uma URL para encurtar."

    if len(url_normalizada) > MAX_ORIGINAL_URL_LENGTH:
        return None, f"A URL deve ter no máximo {MAX_ORIGINAL_URL_LENGTH} caracteres."

    parsed_url = urlparse(url_normalizada)
    if parsed_url.scheme not in {"http", "https"} or not parsed_url.netloc:
        return None, "Informe uma URL válida começando com http:// ou https://."

    return url_normalizada, None


def normalizar_codigo_personalizado(codigo):
    codigo_normalizado = (codigo or "").strip().lower()
    return codigo_normalizado or None


def validar_codigo_personalizado(codigo):
    if codigo is None:
        return None

    if len(codigo) < MIN_CUSTOM_CODE_LENGTH or len(codigo) > MAX_CUSTOM_CODE_LENGTH:
        return (
            f"O código personalizado deve ter entre "
            f"{MIN_CUSTOM_CODE_LENGTH} e {MAX_CUSTOM_CODE_LENGTH} caracteres."
        )

    if not CUSTOM_CODE_PATTERN.fullmatch(codigo):
        return "Use apenas letras sem acento, números, hífen ou underscore no código personalizado."

    if codigo in RESERVED_SLUGS:
        return "Este código é reservado pelo sistema. Escolha outro."

    return None


def slug_reservado(codigo):
    return (codigo or "").lower() in RESERVED_SLUGS
