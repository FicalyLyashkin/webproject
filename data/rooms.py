import datetime
import sqlalchemy
from sqlalchemy import orm
from flask_login import UserMixin
from .db_session import SqlAlchemyBase
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import ForeignKey
from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship


class Room(SqlAlchemyBase, UserMixin):
    __tablename__ = 'rooms'
    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String, nullable=False)
    password = Column(String, nullable=True)
    video_link = Column(String, nullable=True)
    current_time = Column(Float, default=0.0)
    leader_id = Column(Integer, ForeignKey('users.id'))
    leader = relationship('User', backref='led_rooms', foreign_keys=[leader_id])
    users = relationship("User", back_populates="room", foreign_keys="User.room_id")

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)


