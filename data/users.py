import datetime
import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin
from werkzeug.security import generate_password_hash, check_password_hash
from .db_session import SqlAlchemyBase


class User(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'Users'
    status_recommendation = orm.relationship("Status_recommendation", back_populates='user')
    User_ID = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    Name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    Registration_Day = sqlalchemy.Column(sqlalchemy.DateTime,
                                         default=datetime.datetime.now)
    Age_Group = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    Schedule = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    Sex = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    UserName = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    Chat_Id = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    Time = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    Timezone = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    Period = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    Advent_Start = sqlalchemy.Column(sqlalchemy.DateTime, nullable=True)
