from flask import Flask, Blueprint, render_template, request, flash, redirect
from flask_mail import Mail, Message
from flask.helpers import url_for
from .models import User, Role, UserRoles
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from flask_user import roles_required, UserManager, UserMixin

auth = Blueprint('auth', __name__)


@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Contraseña incorrecta', category='error')
        else:
            flash('El Email no existe', category='error')

    return render_template("login.html", user=current_user)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('views.home'))


@auth.route("/sign-up", methods=["GET", "POST"])
def sign_up():
    if request.method == "POST":
        email = request.form.get("email")
        first_name = request.form.get("firstName")
        last_name = request.form.get("lastName")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")
        associate = request.form.get('associate')

        user = User.query.filter_by(email=email).first()
        admin_role = Role.query.filter_by(name="Admin").first()
        member_role = Role.query.filter_by(name="Member").first()
        # admin_role = Role(name="Admin")
        # member_role = Role(name="Member")

        userRoles = [member_role, ]

        if associate == "on":
            userRoles.append(admin_role)

        if user:
            flash('El Email ya existe', category='error')
        elif len(email) < 4:
            flash("El Email debe ser mas largo", category="error")
        elif len(first_name) < 2:
            flash("Nombre debe ser mas largo", category="error")
        elif password1 != password2:
            flash("Las contraseñas deben ser iguales", category="error")
        elif len(password1) < 6:
            flash("La contraseña debe ser mas larga", category="error")
        else:
            new_user = User(email=email, first_name=first_name,
                            password=generate_password_hash(password1, method='sha256'), roles=userRoles)
            db.session.add(new_user)
            db.session.commit()

            # login_user(user, remember=True)
            flash("Cuenta creada!", category="success")
            return redirect(url_for('views.home'))

    return render_template("sign_up.html", user=current_user)
