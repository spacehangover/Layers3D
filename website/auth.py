from flask import Flask, Blueprint, render_template, request, flash, redirect
from flask_mail import Mail, Message
from flask.helpers import url_for
from .models import User, Role, UserRoles
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from flask_user import roles_required, UserManager, UserMixin
import datetime

auth = Blueprint('auth', __name__)
app = Flask(__name__)

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

s = URLSafeTimedSerializer('Thisisasecret!')


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
        # associate = request.form.get('associate')
        terms = request.form.get('terms')
        token = s.dumps(email, salt='email-confirm')
        msg = Message('Confirmar Email',
                      sender='quantumprinting3d@gmail.com', recipients=[email])

        link = url_for('auth.confirm_email', token=token, _external=True)

        msg.body = 'Your link is {}'.format(link)

        user = User.query.filter_by(email=email).first()
        admin_role = Role.query.filter_by(name="Admin").first()
        member_role = Role.query.filter_by(name="Member").first()
        # admin_role = Role(name="Admin")
        # member_role = Role(name="Member")

        userRoles = [member_role, ]

        # if associate == "on":
        #     userRoles.append(admin_role)

        print(type(terms))

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
        elif str(terms) == "None":
            flash("Aceptar terminos y condiciones", category="error")
        else:
            new_user = User(email=email, first_name=first_name, last_name=last_name,
                            password=generate_password_hash(password1, method='sha256'), registered_on=datetime.datetime.now(), roles=userRoles)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            flash("Cuenta creada!", category="success")
            mail.send(msg)
            return redirect(url_for('views.home'))

    return render_template("sign_up.html", user=current_user)


@auth.route('/confirm_email/<token>', methods=["GET", "POST"])
def confirm_email(token):
    try:
        email = s.loads(token, salt='email-confirm', max_age=3600)
        user = User.query.filter_by(email=email).first()
        user.confirmed = True
        user.confirmed_on = datetime.datetime.now()
        db.session.commit()
    except SignatureExpired:
        return '<h1>The token is expired!</h1>'
    return render_template("confirmed.html")


@auth.route("/update/<int:id>", methods=["GET", "POST"])
def update(id):
    user_to_update = User.query.filter_by(id=id).first()
    return render_template("change.html", user=user_to_update)
