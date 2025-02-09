import os
#from fulltext import *
from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user


app = Flask(__name__)
app.config['SECRET_KEY'] = 'appsecretkey'
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
    os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

bootstrap = Bootstrap(app)
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

''' Products Database '''


class Products(db.Model):

    __searchable__ = ['name', 'description', 'price']
    _id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=False)
    description = db.Column(db.String(100), unique=False)
    price = db.Column(db.Integer, unique=False)
    __tablename__ = 'product'


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(80))


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class LoginForm(FlaskForm):
    username = StringField('username', validators=[
                           InputRequired(), Length(min=4, max=15)])
    password = PasswordField('password', validators=[
                             InputRequired(), Length(min=8, max=80)])


class RegisterForm(FlaskForm):
    email = StringField('email', validators=[InputRequired(), Email(
        message='Invalid email'), Length(max=50)])
    username = StringField('username', validators=[
                           InputRequired(), Length(min=4, max=15)])
    password = PasswordField('password', validators=[
                             InputRequired(), Length(min=8, max=80)])


class addProductForm(FlaskForm):
    name = StringField('name', validators=[InputRequired(), Length(max=30)])
    price = StringField('price', validators=[
                        InputRequired(), Length(min=1, max=10)])
    description = StringField('description', validators=[Length(max=100)])


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        admin = form.username.data
        adm_pass = form.password.data
        if admin == "admin" and adm_pass == "password":
            return render_template('admin.html')

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                # login_user(user, remember=form.remember.data)
                return render_template('index.html')

    return render_template('signin.html', form=form)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = generate_password_hash(
            form.password.data, method='sha256')
        new_user = User(username=form.username.data,
                        email=form.email.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        return '<h1>New user has been created!</h1>'

    return render_template('signup.html', form=form)


@app.route('/addProducts', methods=['GET', 'POST'])
def addProducts():
    form = addProductForm()

    if form.validate_on_submit():
        new_product = Products(
            name=form.name.data, price=form.price.data, description=form.description.data)
        db.session.add(new_product)
        db.session.commit()

    return render_template('products.html', form=form)


@app.route('/seeProducts')
def seeProducts():
    return render_template('admin.html', products=Products.query.all(),countProducts = Products.query.count())


@app.route('/seeUsers')
def seeUsers():

    return render_template('admin.html', users=User.query.all(),countUsers = User.query.count())


@app.route('/search', methods=['GET', 'POST'])
def search():
    text = request.form['search']
    prod = Products.query.filter(Products.name.like('%' + text + '%'))
    prod = prod.order_by(Products.name).all()
    return render_template('index.html', search=prod)


@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('index.html', name=current_user.username)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
