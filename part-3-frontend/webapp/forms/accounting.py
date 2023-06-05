from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, PasswordField
from wtforms.validators import DataRequired, ValidationError


class RegistrationForm(FlaskForm):
    login           = StringField("Имя пользователя", validators=[DataRequired()])
    email           = EmailField("Email", validators=[DataRequired()])
    password        = PasswordField("Пароль", validators=[DataRequired()])
    password_repeat = PasswordField("Повторите пароль", validators=[DataRequired()])

    def validate_password_repeat(form, field):
        if field.data != form.password.data:
            raise ValidationError("Пароли должны совпадать!")


class LoginForm(FlaskForm):
    email           = EmailField("Email", validators=[DataRequired()])
    password        = PasswordField("Пароль", validators=[DataRequired()])
