from flask import Blueprint, current_app, redirect, url_for, request, render_template
from flask_login import login_required, current_user, logout_user, login_user

from webapp.db.accounting import register_user, find_user_with_email, AlreadyRegisteredException
from webapp.db.courses import find_courses_created_by, find_comments_left_by
from webapp.forms.accounting import RegistrationForm, LoginForm

accounting_bp = Blueprint("accounting", __name__)


@accounting_bp.route("/logout")
@login_required
def logout():
    current_app.logger.debug("User %s logged out", current_user.login)
    logout_user()
    return redirect(url_for("index"))


@accounting_bp.route("/login", methods=("GET", "POST"))
def login():
    form = LoginForm()
    if request.method == "GET":
        return render_template("login.html", form=form,
                               title="Вход в аккаунт")
    if not form.validate_on_submit():
        errors = ['; '.join(map(str, e)) for e in form.errors.values()]
        return render_template("login.html", form=form, errors=errors,
                               title="Вход в аккаунт")
    user = find_user_with_email(form.email.data)
    if user is not None and user.check_password(form.password.data):
        current_app.logger.debug("User %s logged in", user.login)
        login_user(user)
        return redirect(url_for("index"))
    errors = ["Неверный логин или пароль!"]
    return render_template("login.html", form=form, errors=errors,
                           title="Вход в аккаунт")


@accounting_bp.route("/register", methods=("GET", "POST"))
def register():
    form = RegistrationForm()
    if request.method == "GET":
        return render_template("register.html", form=form,
                               title="Регистрация")
    if not form.validate_on_submit():
        errors = ['; '.join(map(str, e)) for e in form.errors.values()]
        return render_template("register.html", form=form, errors=errors,
                               title="Регистрация")
    try:
        register_user(form.login.data, form.email.data, form.password.data)
    except AlreadyRegisteredException:
        errors = ["Пользователь с таким логином или email уже зарегистрирован!"]
        return render_template("register.html", form=form, errors=errors,
                               title="Регистрация")
    current_app.logger.debug("User %s registred", form.login.data)
    user = find_user_with_email(form.email.data)
    login_user(user)
    return redirect(url_for("index"))


@accounting_bp.route("/")
@login_required
def profile():
    courses = find_courses_created_by(current_user)
    comments = find_comments_left_by(current_user)
    return render_template("profile.html", courses=courses, comments=comments,
                           title="Моя страница")

