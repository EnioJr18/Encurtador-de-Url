import click

from encurtarjr.extensions import db
from encurtarjr.models import User


def register_commands(app):
    @app.cli.group("admin")
    def admin():
        """Administrative commands."""

    @admin.command("promote")
    @click.argument("username")
    def promote(username):
        """Promote an existing user by username."""
        user = User.query.filter_by(username=username.strip()).first()
        if not user:
            raise click.ClickException("Usuario nao encontrado.")

        if user.is_admin:
            click.echo("Usuario ja possui acesso administrativo.")
            return

        user.is_admin = True
        db.session.commit()
        click.echo("Usuario promovido a administrador.")
