import json
import os

from data import db_session
from flask import Flask, request, make_response, render_template, redirect, Response

from data.wood import Wood
from data.width import Width
from data.lists import Lists
from data.pazzle import Pazzle
from data.orders import Orders
from data.clients import Clients
from data.production import Production

from forms.lists import Lists_Form
from forms.pazzles import Pazzle_Form
from forms.orders import create_dynamic_form
from forms.production import ProductionForm


web = Flask(__name__)
web.config['SECRET_KEY'] = 'secret_key'
db_session.global_init("db/data_base.db")


@web.route("/health")
def health():
    return '{"Up!"}'


@web.route("/", methods=['GET', 'POST'])
async def index():
    db_sess = db_session.create_session()
    wood = db_sess.query(Wood).all()
    width = db_sess.query(Width).all()
    lists = db_sess.query(Lists).all()
    pazzle = db_sess.query(Pazzle).all()
    db_sess.close()

    return render_template("index.html", woods=wood, width=width, lists=lists, pazzles=pazzle)


@web.route("/pricelist", methods=['GET', 'POST'])
async def pricelist():
    db_sess = db_session.create_session()
    pazzle = db_sess.query(Pazzle).all()
    db_sess.close()
    return render_template("price_list.html", pazzles=pazzle)


@web.route("/statistica", methods=['GET', 'POST'])
async def statistica():
    db_sess = db_session.create_session()
    orders = db_sess.query(Orders).filter(Orders.status == 'Готов к отгрузке').all()
    result = dict()
    for order in orders:
        goods = order.goods
        goods = goods.split(', ')
        good = []
        for g in goods:
            name, num = g.split(' - ')
            good.append((name, num))
        for name_pazzle, num_pazzle in good:
            if name_pazzle not in result:
                pazzle = db_sess.query(Pazzle).filter(Pazzle.name == name_pazzle).first()
                result[name_pazzle] = {'price': str(int(pazzle.price) * int(num_pazzle)), 'num': str(num_pazzle), 'lists': pazzle.lists}
            else:
                result[name_pazzle]['num'] += num_pazzle
        res = []
        for key in result:
            res.append((key, result[key]))
    db_sess.close()
    return render_template("statistics.html", stat=res)


@web.route("/orders", methods=['GET', 'POST'])
async def orders():
    db_sess = db_session.create_session()
    order = db_sess.query(Orders).all()
    result = []
    for ord in order:
        goods = ord.goods
        goods = goods.split(', ')
        good = []
        for g in goods:
            name, num = g.split(' - ')
            good.append((name, num))
        result.append((ord, good))
    db_sess.close()
    return render_template("orders.html", orders=result)


@web.route("/tasks", methods=['GET', 'POST'])
async def tasks():
    db_sess = db_session.create_session()
    production = db_sess.query(Production).all()
    result = []
    for i in range(len(production)):
        prod = production[i]
        order = db_sess.query(Orders).filter(Orders.id == prod.id_order).first()
        goods = order.goods
        goods = goods.split(', ')
        good = []
        for g in goods:
            name, num = g.split(' - ')
            good.append((name, num))
        result.append((prod, good))
    db_sess.close()
    return render_template("production.html", orders=result)


@web.route('/task/<int:id>', methods=['GET', 'POST'])
async def edit_task(id):
    db_sess = db_session.create_session()
    form = ProductionForm()
    if request.method == "GET":
        prod = db_sess.query(Production).filter(Production.id == id).first()
        if prod:
            form.status.data = prod.status
            form.date_started.data = prod.date_started
            form.date_ended.data = prod.date_ended
            db_sess.close()
        else:
            return not_found_error(f"Заказ с ID {id} не найдена")
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        prod = db_sess.query(Production).filter(Production.id == id).first()
        if prod:
            prod.status = form.status.data
            prod.date_started = form.date_started.data
            prod.date_ended = form.date_ended.data
            db_sess.commit()
            if form.status.data == 'Принято в производство':
                db_sess = db_session.create_session()
                prod = db_sess.query(Production).filter(Production.id == id).first()
                order = db_sess.query(Orders).filter(Orders.id == prod.id_order).first()
                order.status = "На производстве"
                db_sess.commit()
                db_sess.close()
                return redirect('/orders')
            if form.status.data == 'Выполнен':
                db_sess = db_session.create_session()
                prod = db_sess.query(Production).filter(Production.id == id).first()
                order = db_sess.query(Orders).filter(Orders.id == prod.id_order).first()
                order.status = "Готов к отгрузке"
                db_sess.commit()
                db_sess.close()
                return redirect('/orders')
            db_sess.close()
            return redirect("/tasks")
        else:
            return not_found_error(f"Заказ с ID {id} не найдена")
    return render_template('product.html',
                            title='Редактирование задания на производство',
                            form=form)


@web.route('/order', methods=['GET', 'POST'])
def add_order():
    db_sess = db_session.create_session()
    names = db_sess.query(Clients).all()
    pazzles = db_sess.query(Pazzle).all()
    form = create_dynamic_form(pazzles)
    form.client.choices = [g.name for g in names]
    if form.validate_on_submit():
        goods = []
        count = 0
        for key, field in form._fields.items():
            if key not in['status', 'client', 'date', 'submit', 'csrf_token']:
                if field.data != 0:
                    lab = str(field.label)
                    k = 0
                    label = ''
                    for i in lab:
                        if i == '<' or i == '>':
                            k += 1
                        if k == 2:
                            label += i
                    count += field.data
                    goods.append(str(label)[1:] + ' - ' + str(field.data))
        if count == 0:
            return render_template('order.html', title='Добавление заказа',
                                   form=form, message="Нужно выбрать как минимум 1 товар")
        goods = ', '.join(goods)
        order = Orders(
            status=form.status.data,
            client=form.client.data,
            date=form.date.data,
            goods=goods
        )
        db_sess.add(order)
        db_sess.commit()
        if form.status.data == 'Согласовано с клиентом':
            prod = Production(
                status="",
                id_order=order.id
            )
            db_sess.add(prod)
            db_sess.commit()
            db_sess.close()
            return redirect('/orders')
        db_sess.close()
        return redirect('/orders')
    return render_template('order.html', title='Добавление заказа', form=form)


@web.route('/order/<int:id>', methods=['GET', 'POST'])
async def edit_order(id):
    db_sess = db_session.create_session()
    names = db_sess.query(Clients).all()
    pazzles = db_sess.query(Pazzle).all()
    form = create_dynamic_form(pazzles)
    form.client.choices = [g.name for g in names]
    if request.method == "GET":
        order = db_sess.query(Orders).filter(Orders.id == id).first()
        if order:
            goods = order.goods
            goods = goods.split(', ')
            good = []
            for g in goods:
                name, num = g.split(' - ')
                good.append((name, num))
            form.status.data = order.status
            form.client.data = order.client
            form.date.data = order.date
            count = 0
            for key, field in form._fields.items():
                if key not in ['status', 'client', 'date', 'submit', 'csrf_token']:
                    if field.data != 0:
                        field.data = int(good[count][1])
                        count += 1
            db_sess.close()
        else:
            return not_found_error(f"Заказ с ID {id} не найдена")
    if form.validate_on_submit():
        order = db_sess.query(Orders).filter(Orders.id == id).first()
        if order:
            order.status = form.status.data
            order.client = form.client.data
            order.data = form.date.data
            goods = []
            for key, field in form._fields.items():
                if key not in ['status', 'client', 'date', 'submit', 'csrf_token']:
                    if field.data != 0:
                        lab = str(field.label)
                        k = 0
                        label = ''
                        for i in lab:
                            if i == '<' or i == '>':
                                k += 1
                            if k == 2:
                                label += i
                        goods.append(str(label)[1:] + ' - ' + str(field.data))
            goods = ', '.join(goods)
            order.goods = goods
            db_sess.commit()
            if form.status.data == 'Согласовано с клиентом':
                prod = Production(
                    status="",
                    id_order=order.id
                )
                db_sess.add(prod)
                db_sess.commit()
                db_sess.close()
                return redirect('/orders')
            return redirect("/orders")
        else:
            db_sess.close()
            return not_found_error(f"Заказ с ID {id} не найдена")
    return render_template('order.html',
                            title='Редактирование заказа',
                            form=form)


@web.route('/order_delete/<int:id>', methods=['GET', 'POST'])
async def order_delete(id):
    db_sess = db_session.create_session()
    order = db_sess.query(Orders).filter(Orders.id == id).first()
    if order:
        db_sess.delete(order)
        db_sess.commit()
        db_sess.close()
        return redirect('/orders')
    else:
        return not_found_error(f"Заказ с ID {id} не найдена")


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
    # web.run(port=8080, host='127.0.0.1', debug=True)
    port = int(os.environ.get("PORT", 5000))
    web.run(host='0.0.0.0', port=port)
