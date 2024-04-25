from flask_wtf import FlaskForm
from wtforms import *


class CreateRoomForm(FlaskForm):
    code = StringField("Код комнаты")
    password = PasswordField("Придумайте пароль для комнаты")
    submit = SubmitField('Войти')
