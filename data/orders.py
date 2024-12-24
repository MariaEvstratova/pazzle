import sqlalchemy
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin
from .db_session import SqlAlchemyBase
import datetime


class Orders(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'orders'
    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    status = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    client = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
    goods = sqlalchemy.Column(sqlalchemy.String, nullable=True)