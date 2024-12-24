from flask_wtf import FlaskForm

from wtforms import StringField
from wtforms.fields import SelectField, SubmitField, IntegerField
from wtforms.validators import DataRequired
from data.lists import Lists
from data import db_session


class Lists_Form(FlaskForm):
    wood = SelectField('Вид древесины', choices=["Береза", "Сосна", "Клен", "Махагон", "Дуб", "Липа", "Тик", "Вишня"])
    width = SelectField('Вид древесины', choices=["3 мм", "4 мм", "6 мм", "9 мм"])
    submit = SubmitField('Применить')
