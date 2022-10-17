from datetime import datetime, timedelta
from flask import Flask, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
import os
import config

app = Flask(__name__)

app.config['SECRET_KEY'] = 'secret'
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{config.DB_LOGIN}:{config.DB_PASS}@{config.DB_HOST}:{config.DB_PORT}/{config.DB_NAME}?charset=utf8mb4'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
app_root = os.path.dirname(os.path.abspath(__file__))

# DB Model USER
class Users(db.Model):
    id = db.Column(db.String(200), primary_key=True)
    login = db.Column(db.String(200), nullable=True)
    fullname = db.Column(db.String(200), nullable=True)
    phone = db.Column(db.String(200), nullable=True)
    experience = db.Column(db.String(400), nullable=True)
    job = db.Column(db.String(400), nullable=True)
    region = db.Column(db.String(400), nullable=True)
    city = db.Column(db.String(400), nullable=True)
    key = db.Column(db.String(400), nullable=True)
    notification = db.Column(db.JSON, nullable=True)
    # json structure {'status': (yes, no), 'filter': {}}
    datetime = db.Column(db.DateTime, nullable=False, default=datetime.now())

# DB model Objects
class Objects(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    user = db.Column(db.String(200), db.ForeignKey('users.id'), nullable=False)
    region = db.Column(db.String(400), nullable=True)
    city = db.Column(db.String(400), nullable=True)
    area = db.Column(db.String(400), nullable=True)
    address = db.Column(db.String(400), nullable=True)
    street = db.Column(db.String(400), nullable=True)
    rooms = db.Column(db.Integer(), nullable=True)
    stage = db.Column(db.Integer(), nullable=True)
    description = db.Column(db.Text(), nullable=True)
    price = db.Column(db.String(200), nullable=True)
    quadrature = db.Column(db.Float(), nullable=True)
    property_type = db.Column(db.String(400), nullable=True)
    number_of_storeys = db.Column(db.Integer(), nullable=True)
    phone = db.Column(db.String(200), nullable=True)
    date_end = db.Column(db.DateTime, nullable=False, default=datetime.now() + timedelta(days=30))
    datetime = db.Column(db.DateTime, nullable=False, default=datetime.now())

# DB model Keys
class AccessKeys(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    key = db.Column(db.String(400), nullable=True)
    user = db.Column(db.String(200), db.ForeignKey('users.id'), nullable=True)
    datetime = db.Column(db.DateTime, nullable=False, default=datetime.now())
    
class UserAdmin(db.Model, UserMixin):
    id = db.Column(db.Integer(), primary_key=True)
    login = db.Column(db.String(128), nullable=False, unique=True)
    password = db.Column(db.String(128), nullable=False)

with app.app_context():
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['JSON_AS_ASCII'] = False
    # db.create_all()
    
    # Session(app)