import datetime
import sqlalchemy
from sqlalchemy import orm
from flask_login import UserMixin
from .db_session import SqlAlchemyBase
from werkzeug.security import generate_password_hash, check_password_hash


class Room(SqlAlchemyBase, UserMixin):
    __tablename__ = 'rooms'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    code = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    video_link = sqlalchemy.Column(sqlalchemy.String,
                              index=True, unique=True, nullable=False)
    members = sqlalchemy.Column(sqlalchemy.String, nullable=False)

