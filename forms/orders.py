from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, SubmitField, DateTimeField
from wtforms.validators import DataRequired
import datetime


class OrdersForm(FlaskForm):
    status = SelectField('Статус заказа', choices=["Черновик", "Согласовано с клиентом"])
    client = SelectField("Клиент")
    date = DateTimeField('Дата выполнения', default=datetime.datetime.now)
    submit = SubmitField('Применить')


def create_dynamic_form(pazzles):
    class DynamicOrdersForm(OrdersForm):
        pass
    for pazzle in pazzles:
        setattr(DynamicOrdersForm, str(pazzle.id), IntegerField(pazzle.name, default=0))
    return DynamicOrdersForm()


