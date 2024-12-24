from flask_wtf import FlaskForm
from wtforms import StringField, SelectField
from wtforms import SubmitField, IntegerField
from data import db_session
from data.lists import Lists

class Pazzle_Form(FlaskForm):
    name = StringField("Название пазла")
    lists = SelectField('Фанерный лист')
    num_details = IntegerField('Количество деталей, шт')
    price = IntegerField('Цена, рубли')
    submit = SubmitField('Применить')


def lists(request):
    db_sess = db_session.create_session()
    list = db_sess.query(Lists).all()
    form = Pazzle_Form(request.post, obj=list)
    form.lists.choices = [g.name for g in list]