from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, SubmitField, DateTimeField
from wtforms.validators import DataRequired
import datetime


class ProductionForm(FlaskForm):
    status = SelectField('Состояние', choices=["Принято в производство", "Выполнен"])
    date_started = DateTimeField('Дата регистрации заказа', default=datetime.datetime.now)
    date_ended = DateTimeField('Дата выполнения', default=datetime.datetime.now)
    submit = SubmitField('Применить')


