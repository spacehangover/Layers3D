from flask import Blueprint, render_template, request, flash, redirect, Response
from flask.helpers import url_for
from flask_mail import Mail, Message
from .models import User, Product
from website import create_app
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from . import db, allowed_file
from flask_login import login_user, login_required, logout_user, current_user
from flask_user import roles_required, UserManager, UserMixin
import os
import random

views = Blueprint('views', __name__)
app = create_app()
mail = Mail(app)


@views.route('/')
def home():
    return render_template("home.html", user=current_user)


@views.route('/join')
def join():
    return render_template("join.html", user=current_user)


@views.route('/tienda')
def tienda():
    # products = Product.query.all()
    return render_template("shop.html", user=current_user, products=Product.query.all())


@views.route('/pedidos')
@login_required
def pedidos():
    return render_template("pedidos.html", user=current_user)


@views.route('/add', methods=["GET", "POST"])
@login_required
def add():
    products = Product.query.all()
    if request.method == "POST":
        if current_user.associate == "on":
            productName = request.form.get("productName")
            productPrice = request.form.get("productPrice")
            pic = request.files['pic']

            if pic and allowed_file(pic.filename):
                filename = secure_filename(pic.filename)
                splitFilename = os.path.splitext(filename)
                newFilename = splitFilename[0] + \
                    str(random.randint(1, 10000000)) + splitFilename[1]
                print(newFilename)
                image_name = os.path.join("static/products/", newFilename)
                pic.save(os.path.join(
                    "E:\Coding\QuantumWeb\QuantumFlask\website\static\products", newFilename))

            if not pic:
                flash('Agregar foto', category='error')
            else:
                newProduct = Product(product_name=productName,
                                     product_price=productPrice, image_name=image_name)
                db.session.add(newProduct)
                db.session.commit()
                flash('Producto añadido', category='success')
        else:
            flash('No eres socio', category='error')
    return render_template('add.html', user=current_user)


@views.route('/changeprice', methods=["GET", "POST"])
def change_price():
    products = Product.query.all()
    if request.method == "POST":
        productName = request.form.get("productName")
        newProductPrice = request.form.get("productPrice")

        product_to_change = Product.query.filter_by(
            product_name=productName).first()

        product_to_change.product_price = newProductPrice

        db.session.commit()
        flash('Producto actualizado', category='success')

    return render_template('change.html', user=current_user)


@views.route("/admin", methods=["GET", "POST"])
@login_required
@roles_required("Admin")
def admin_dashboard():
    return "Hello admin"
