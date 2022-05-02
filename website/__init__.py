from flask import Flask, jsonify, url_for
from flask_mail import Mail, Message
from flask_sqlalchemy import SQLAlchemy
from os import path
import os
from flask_login import LoginManager
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from flask_mail import Mail, Message
from flask_user import login_required, SQLAlchemyAdapter, UserManager, UserMixin

db = SQLAlchemy()
DB_NAME = "database.db"


UPLOAD_FOLDER = 'E:/Coding/QuantumWeb3.0/website/static/products/'
PRODUCT_FOLDER = 'E:/Coding/QuantumWeb3.0/website/static/products/'

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = '21'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['PRODUCT_FOLDER'] = PRODUCT_FOLDER
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
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
    db.init_app(app)

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    from .models import User, Role, UserRoles

    db_adapter = SQLAlchemyAdapter(db,  User)
    user_manager = UserManager(db_adapter, app)

    create_database(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app


def create_database(app):
    from .models import User, Role, UserRoles
    if not path.exists('website/' + DB_NAME):
        db.create_all(app=app)
        print('Created database!')
        with app.app_context():
            admin_role = Role(name="Admin")
            member_role = Role(name="Member")
            partner_role = Role(name="Partner")
            db.session.add(admin_role)
            db.session.add(member_role)
            db.session.add(partner_role)
            create_admin()
            db.session.commit()


def create_admin():
    from .models import User, Role, UserRoles
    from werkzeug.security import generate_password_hash, check_password_hash
    import datetime
    admin_role = Role.query.filter_by(name="Admin").first()
    member_role = Role.query.filter_by(name="Member").first()
    userRoles = [member_role, admin_role]
    admin_user = User(email="quantumprinting3d@gmail.com", first_name="Quantum", last_name="Printing",
                      password=generate_password_hash("Peugeot307xtp", method='sha256'), registered_on=datetime.datetime.now(), roles=userRoles)
    db.session.add(admin_user)
    admin_user.confirmed = True
    admin_user.confirmed_on = datetime.datetime.now()
    db.session.commit()
