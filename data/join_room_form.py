from flask_wtf import FlaskForm
from wtforms import *


class JoinRoomForm(FlaskForm):
    code = StringField("Код комнаты")
    password = PasswordField("Пароль комнаты")
    submit = SubmitField('Войти')
