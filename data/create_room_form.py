from flask_wtf import FlaskForm
from wtforms import *


class CreateRoomForm(FlaskForm):
    code = StringField("Название комнаты")
    password = PasswordField("Придумайте пароль для комнаты")
    submit = SubmitField('Создать')
