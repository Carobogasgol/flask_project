import os
import random
import sys

import requests
from flask import Flask, render_template, redirect, request, url_for
from data1 import db_session
from data1.users import User
from data1.cities import City
from forms.user import RegisterForm, LoginForm, SearchForm
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from Samples import geocoder

CITIES = []


app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)


def main():
    global CITIES
    db_session.global_init("db/geoguesser.db")
    db_sess = db_session.create_session()

    city = City()
    city.city = 'Дерби'
    db_sess.add(city)
    db_sess.commit()

    city = City()
    city.city = 'Псков'
    db_sess.add(city)
    db_sess.commit()

    city = City()
    city.city = 'Сингапур'
    db_sess.add(city)
    db_sess.commit()

    city = City()
    city.city = 'Бергамо'
    db_sess.add(city)
    db_sess.commit()

    city = City()
    city.city = 'Прага'
    db_sess.add(city)
    db_sess.commit()

    for city in db_sess.query(City).all():
        CITIES.append(city)

    app.run()


@app.route("/")
def index():
    db_sess = db_session.create_session()
    return render_template("index.html")


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data,
            about=form.about.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect('/geoguesser')
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/geoguesser')
def geoguesser():
    form = SearchForm()
    current_city = random.choice(CITIES)
    lat, lon = geocoder.get_coordinates(current_city)
    ll_spn = f'll={lat},{lon}&spn=0.016457,0.00619'
    ll_spn2 = f'll={lat + 0.05},{lon}&spn=0.016457,0.00619'
    ll_spn3 = f'll={lat},{lon + 0.1}&spn=0.016457,0.00619'
    map_type = "map"

    map_request = f"http://static-maps.yandex.ru/1.x/?{ll_spn}&l={map_type}"
    map_request2 = f"http://static-maps.yandex.ru/1.x/?{ll_spn2}&l={map_type}"
    map_request3 = f"http://static-maps.yandex.ru/1.x/?{ll_spn3}&l={map_type}"

    if form.validate_on_submit():
        if form.search.data == current_city:
            return redirect(url_for('success'))
        else:
            return redirect(url_for('fail'))

    return render_template('geoguesser.html', first_image=map_request, second_image=map_request2,
                           third_image=map_request3, form=form)


@app.route('/success')
def success():
    return 'Правильно'


@app.route('/fail')
def fail():
    return 'Неправильно'


if __name__ == '__main__':
    main()
