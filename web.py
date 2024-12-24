import json
import threading
import random
import datetime
# from datetime import datetime
from pyexpat.errors import messages
import requests

from data import db_session
from flask import Flask, request, make_response, render_template, redirect, Response

from data.wood import Wood
from data.width import Width
from data.lists import Lists
from data.pazzle import Pazzle

from forms.lists import Lists_Form
from forms.pazzles import Pazzle_Form, lists


web = Flask(__name__)
web.config['SECRET_KEY'] = 'secret_key'
db_session.global_init("db/data_base.db")


@web.route("/", methods=['GET', 'POST'])
async def index():
    db_sess = db_session.create_session()
    wood = db_sess.query(Wood).all()
    width = db_sess.query(Width).all()
    lists = db_sess.query(Lists).all()
    pazzle = db_sess.query(Pazzle).all()
    db_sess.close()

    return render_template("index.html", woods=wood, width=width, lists=lists, pazzles=pazzle)


@web.route('/list', methods=['GET', 'POST'])
def add_list():
    form = Lists_Form()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        name_new = form.wood.data + ', ' + str(form.width.data)
        if db_sess.query(Lists).filter(Lists.name == name_new).first():
            return render_template('list.html', title='Добавление листа',
                                   form=form, message="Такой лист уже есть")
        list = Lists(
            name=name_new,
            wood=form.wood.data,
            width=form.width.data
        )
        db_sess.add(list)
        db_sess.commit()
        db_sess.close()
        return redirect('/')
    return render_template('list.html', title='Добавление листа',
                            form=form)


@web.route('/list/<int:id>', methods=['GET', 'POST'])
async def edit_list(id):
    form = Lists_Form()
    db_sess = db_session.create_session()
    if request.method == "GET":
        list = db_sess.query(Lists).filter(Lists.id == id).first()
        if list:
            form.wood.data = list.wood
            form.width.data = list.width
            db_sess.commit()
            db_sess.close()
        else:
            return not_found_error(f"Лист с ID {id} не найдена")
    if form.validate_on_submit():
        list = db_sess.query(Lists).filter(Lists.id == id).first()
        if list:
            list.name = form.wood.data + ', ' + form.width.data
            list.wood = form.wood.data
            list.width = form.width.data
            db_sess.commit()
            db_sess.close()
            return redirect('/')
        else:
            return not_found_error(f"Лист с ID {id} не найдена")
    return render_template('list.html',
                            title='Редактирование листа',
                            form=form)


@web.route('/list_delete/<int:id>', methods=['GET', 'POST'])
async def list_delete(id):
    db_sess = db_session.create_session()
    list = db_sess.query(Lists).filter(Lists.id == id).first()
    if list:
        db_sess.delete(list)
        db_sess.commit()
        db_sess.close()
        return redirect('/')
    else:
         return not_found_error(f"Лист с ID {id} не найдена")


@web.route('/pazzle', methods=['GET', 'POST'])
def add_pazzle():
    db_sess = db_session.create_session()
    form = Pazzle_Form()
    list = db_sess.query(Lists).all()
    form.lists.choices = [g.name for g in list]
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        if db_sess.query(Pazzle).filter(Pazzle.name == form.name.data).first():
            return render_template('pazzle.html', title='Добавление пазла',
                                   form=form, message="Такой пазл уже есть")
        pazzle = Pazzle(
            name=form.name.data,
            lists=form.lists.data,
            num_details=form.num_details.data,
            picture=''
        )
        db_sess.add(pazzle)
        db_sess.commit()
        db_sess.close()
        return redirect('/')
    return render_template('pazzle.html', title='Добавление пазла',
                            form=form)


@web.route('/pazzle/<int:id>', methods=['GET', 'POST'])
async def edit_pazzle(id):
    form = Pazzle_Form()
    db_sess = db_session.create_session()
    list = db_sess.query(Lists).all()
    form.lists.choices = [g.name for g in list]
    if request.method == "GET":
        pazzle = db_sess.query(Pazzle).filter(Pazzle.id == id).first()
        if pazzle:
            form.name.data = pazzle.name
            form.lists.data = pazzle.lists
            form.num_details.data = pazzle.num_details
            form.price.data = pazzle.price
            db_sess.commit()
            db_sess.close()
        else:
            return not_found_error(f"Лист с ID {id} не найдена")
    if form.validate_on_submit():
        pazzle = db_sess.query(Pazzle).filter(Pazzle.id == id).first()
        if pazzle:
            pazzle.name = form.name.data
            pazzle.lists = form.lists.data
            pazzle.num_details = form.num_details.data
            pazzle.price = form.price.data
            db_sess.commit()
            db_sess.close()
            return redirect('/')
        else:
            return not_found_error(f"Пазл с ID {id} не найдена")
    return render_template('pazzle.html',
                            title='Редактирование пазла',
                            form=form)


@web.route('/pazzle_delete/<int:id>', methods=['GET', 'POST'])
async def pazzle_delete(id):
    db_sess = db_session.create_session()
    pazzle = db_sess.query(Pazzle).filter(Pazzle.id == id).first()
    if pazzle:
        db_sess.delete(pazzle)
        db_sess.commit()
        db_sess.close()
        return redirect('/')
    else:
         return not_found_error(f"Пазл с ID {id} не найдена")


def unauthorize_error(message):
    error = {'error': message}
    response = make_response(json.dumps(error, ensure_ascii=False))
    response.status_code = 403
    return response


def not_found_error(message):
    error = {'error': message}
    response = make_response(json.dumps(error, ensure_ascii=False))
    response.status_code = 404
    return response


if __name__ == '__main__':
    web.run(port=8080, host='127.0.0.1', debug=True)
    # port = int(os.environ.get("PORT", 5000))
    # app.run(host='0.0.0.0', port=port)
