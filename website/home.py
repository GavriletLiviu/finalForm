from flask import  Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user

home = Blueprint('homes', __name__)

@views.route('/', methods=['GET', 'POST'])
@login_required
def home():