from __future__ import annotations

"""Rotas de autenticação e definição do formulário de login."""

from typing import cast

from flask import Blueprint, current_app, flash, redirect, render_template, session, url_for
from flask_wtf import FlaskForm  # pyright: ignore[reportMissingTypeStubs]
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Length
from werkzeug.security import check_password_hash

from app.services.db import DBError, get_user_by_login

auth_bp = Blueprint("auth", __name__)


class LoginForm(FlaskForm):
    """Formulário usado para autenticar um usuário por login ou e-mail."""

    login = StringField("Usuario ou e-mail", validators=[DataRequired(), Length(max=120)])
    password = PasswordField("Senha", validators=[DataRequired(), Length(max=128)])
    submit = SubmitField("Entrar")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """Renderiza o login e inicia a sessão quando as credenciais são válidas."""
    session_data = cast(dict[str, object], session)

    if session_data.get("user_id") is not None:
        return redirect(url_for("agenda.index"))

    form = LoginForm()
    if form.validate_on_submit():  # pyright: ignore[reportUnknownMemberType]
        database_path = cast(str, current_app.config["DATABASE_PATH"])
        login_or_email = (form.login.data or "").strip()
        password = form.password.data or ""

        try:
            user = get_user_by_login(database_path, login_or_email)
        except DBError:
            raise

        # Mantém a autenticação explícita: busca o usuário e depois valida o hash da senha.
        if user and check_password_hash(user.password_hash, password):
            session_data["user_id"] = user.id
            session_data["user_login"] = user.login
            return redirect(url_for("agenda.index"))

        flash("Usuario ou senha invalidos.", "error")
        current_app.logger.warning(
            "event=login_failed, error_type=INVALID_CREDENTIALS, detail=invalid credentials"
        )

    return render_template("login.html", form=form)


@auth_bp.route("/logout", methods=["GET"])
def logout():
    """Limpa a sessão atual e redireciona o usuário para o login."""
    session.clear()
    return redirect(url_for("auth.login"))
