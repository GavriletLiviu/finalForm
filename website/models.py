from . import db
from flask_login import UserMixin

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(20), nullable=False)
    lastname = db.Column(db.String(20), nullable=False)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    country = db.Column(db.String(20), nullable=False)
    is_admin = db.Column(db.Integer, nullable=False)
    ##is_active = db.Column(db.Boolean)

class Causes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), unique=True)
    picture = db.Column(db.String(100), nullable=True)
    description = db.Column(db.String(500))
    donated_amount = db.Column(db.Integer)
    remaining_amount = db.Column(db.Integer)