import sqlalchemy
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin
from .db_session import SqlAlchemyBase
from data import db_session
from data.lists import Lists


class Pazzle(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'pazzles'
    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    lists = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    num_details = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    price = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    picture = sqlalchemy.Column(sqlalchemy.String, nullable=True)