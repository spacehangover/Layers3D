from flask import Blueprint, render_template, request, flash, redirect, Response
from flask.helpers import url_for
from flask_mail import Mail, Message
from website.auth import login
from .models import User, Product, Role
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

mail_settings = {
    "MAIL_SERVER": 'smtp.gmail.com',
    "MAIL_PORT": 465,
    "MAIL_USE_TLS": False,
    "MAIL_USE_SSL": True,
    "MAIL_USERNAME": "quantumprinting3d@gmail.com",
    "MAIL_PASSWORD": "Peugeot307xtp"
}
app.config.update(mail_settings)
mail = Mail(app)


@views.route('/', methods=["GET", "POST"])
def home():
    if request.method == "POST":
        client_name = request.form.get("name")
        client_email = request.form.get("email")
        subject = request.form.get("subject")
        message = request.form.get("message")

        msg = Message('Nueva consulta de' + client_email,
                      sender='quantumprinting3d@gmail.com', recipients=["quantumprinting3d@gmail.com"])
        msg.body = message
        mail.send(msg)
        flash('Mensaje enviado', category='success')
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
# @login_required
def add():
    products = Product.query.all()
    if request.method == "POST":
        productName = request.form.get("productName")
        productPrice = request.form.get("productPrice")
        pic = request.files['pic']

        # if pic and allowed_file(pic.filename):
        #     filename = secure_filename(pic.filename)
        #     splitFilename = os.path.splitext(filename)
        #     newFilename = splitFilename[0] + \
        #         str(random.randint(1, 10000000)) + splitFilename[1]
        #     print(newFilename)
        #     image_path = os.path.join("static/products/", newFilename)
        #     pic.save(os.path.join(
        #         "E:\Coding\QuantumWeb\QuantumFlask\website\static\products", newFilename))

        if not pic:
            flash('Agregar foto', category='error')
        else:
            newProduct = Product(product_name=productName,
                                 product_price=productPrice)
            db.session.add(newProduct)
            db.session.commit()

            if allowed_file(pic.filename):
                filename = secure_filename(pic.filename)
                splitFilename = os.path.splitext(filename)
                newFilename = str(newProduct.id) + splitFilename[1]
                print(newFilename)
                image_path = "static/products/" + newFilename
                pic.save(app.config['UPLOAD_FOLDER'] + newFilename)
                newProduct.image_path = image_path
                flash('product added', category='success')
                print(newFilename)
                print(image_path)
                db.session.commit()

    return render_template('add.html', user=current_user)


@ views.route('/changeprice', methods=["GET", "POST"])
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


@ views.route("/admin", methods=["GET", "POST"])
@ login_required
@ roles_required("Admin")
def admin_dashboard():
    return render_template("dashboardtemp.html", roles=Role.query.all(), users=User.query.all(), current_user=current_user)


@ views.route("/database", methods=["GET", "POST"])
@ login_required
@ roles_required("Admin")
def database():
    return render_template("database_table.html", roles=Role.query.all(), users=User.query.all(), user=current_user, products=Product.query.all())
