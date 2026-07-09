from dataclasses import dataclass

from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from encurtarjr.extensions import db
from encurtarjr.models import URL
from encurtarjr.utils import (
    gerar_codigo_curto,
    normalizar_codigo_personalizado,
    slug_reservado,
    validar_codigo_personalizado,
    validar_url_original,
)


MAX_AUTO_CODE_ATTEMPTS = 10


@dataclass
class ShortenResult:
    success: bool
    message: str | None = None
    short_code: str | None = None


def gerar_codigo_unico():
    for _ in range(MAX_AUTO_CODE_ATTEMPTS):
        codigo = gerar_codigo_curto()
        if slug_reservado(codigo):
            continue
        if not URL.query.filter_by(short_code=codigo).first():
            return codigo

    return None


def criar_url_encurtada(original_url, custom_url=None, user_id=None):
    url_original, erro_url = validar_url_original(original_url)
    if erro_url:
        return ShortenResult(success=False, message=erro_url)

    codigo_curto = normalizar_codigo_personalizado(custom_url)
    erro_codigo = validar_codigo_personalizado(codigo_curto)
    if erro_codigo:
        return ShortenResult(success=False, message=erro_codigo)

    codigo_personalizado_informado = codigo_curto is not None

    if codigo_curto:
        existente = URL.query.filter_by(short_code=codigo_curto).first()
        if existente:
            return ShortenResult(success=False, message="O código curto personalizado já está em uso. Tente outro.")
    else:
        codigo_curto = gerar_codigo_unico()
        if not codigo_curto:
            return ShortenResult(success=False, message="Não foi possível gerar um código curto agora. Tente novamente.")

    nova_url = URL(original_url=url_original, short_code=codigo_curto, user_id=user_id)

    try:
        db.session.add(nova_url)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        if codigo_personalizado_informado:
            return ShortenResult(success=False, message="Este código curto já está em uso. Escolha outro.")
        return ShortenResult(
            success=False,
            message="Não foi possível salvar o link por colisão de código. Tente novamente.",
        )
    except SQLAlchemyError:
        db.session.rollback()
        return ShortenResult(success=False, message="Erro inesperado ao salvar o link. Tente novamente.")

    return ShortenResult(success=True, short_code=codigo_curto)


def registrar_clique(url_entry):
    URL.query.filter_by(id=url_entry.id).update({
        URL.click_count: URL.click_count + 1,
        URL.acesso_data: db.func.now(),
    })
    db.session.commit()
