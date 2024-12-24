import sqlalchemy
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin
from .db_session import SqlAlchemyBase
import datetime


class Production(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'production'
    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    status = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    id_order = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    date_started = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
    date_ended = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)