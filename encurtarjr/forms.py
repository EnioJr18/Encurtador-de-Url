from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField
from wtforms.validators import DataRequired, Length, Optional


class RegisterForm(FlaskForm):
    username = StringField("Usuário", validators=[DataRequired(), Length(max=150)])
    password = PasswordField("Senha", validators=[DataRequired(), Length(max=200)])


class LoginForm(FlaskForm):
    username = StringField("Usuário", validators=[DataRequired(), Length(max=150)])
    password = PasswordField("Senha", validators=[DataRequired(), Length(max=200)])


class ShortenURLForm(FlaskForm):
    url = StringField("URL", validators=[DataRequired(), Length(max=500)])
    custom_url = StringField("Código personalizado", validators=[Optional(), Length(max=50)])
