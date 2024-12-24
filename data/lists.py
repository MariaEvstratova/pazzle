import sqlalchemy
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin
from .db_session import SqlAlchemyBase


class Lists(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'lists'
    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    wood = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    width = sqlalchemy.Column(sqlalchemy.String, nullable=True)