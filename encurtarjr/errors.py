import logging

from flask import current_app, render_template, request
from flask_wtf.csrf import CSRFError


def configure_logging(app):
    """Configure application logs without exposing request or configuration data."""
    log_level_name = app.config.get("LOG_LEVEL", "INFO").upper()
    log_level = getattr(logging, log_level_name, logging.INFO)

    if not app.logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(
            logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
        )
        app.logger.addHandler(handler)

    app.logger.setLevel(log_level)


def register_error_handlers(app):
    @app.errorhandler(CSRFError)
    def handle_csrf_error(error):
        current_app.logger.warning(
            "CSRF validation failed for %s %s", request.method, request.path
        )
        return render_template(
            "errors/400.html",
            message="Sua sessao expirou ou o formulario enviado e invalido. Tente novamente.",
        ), 400

    @app.errorhandler(400)
    def handle_bad_request(error):
        current_app.logger.warning("Bad request for %s %s", request.method, request.path)
        return render_template("errors/400.html"), 400

    @app.errorhandler(404)
    def handle_not_found(error):
        current_app.logger.info("Page not found: %s", request.path)
        return render_template("errors/404.html"), 404

    @app.errorhandler(429)
    def handle_rate_limit(error):
        current_app.logger.warning("Rate limit reached for %s %s", request.method, request.path)
        return render_template("errors/429.html"), 429

    @app.errorhandler(500)
    def handle_internal_server_error(error):
        current_app.logger.error("Unhandled application error", exc_info=error)
        return render_template("errors/500.html"), 500
