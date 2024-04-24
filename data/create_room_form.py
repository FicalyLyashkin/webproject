from flask_wtf import FlaskForm
from wtforms import *
from wtforms.validators import DataRequired


class CreateRoomForm(FlaskForm):
    code = StringField("Код")
    video_link = StringField('Ссылка на видео')
    submit = SubmitField('Войти')
