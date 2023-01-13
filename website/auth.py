import filecmp
import fileinput
import os
from flask import  Blueprint, render_template, request, flash, redirect, url_for
from .models import User, Causes
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename
from werkzeug.datastructures import  FileStorage
import pathlib

auth = Blueprint('auths', __name__)
UPLOAD_FOLDER = '/static/images'


@auth.route('/', methods=['GET', 'POST'])
@login_required
def home():    
    return render_template("login.html", user=current_user)

@auth.route('/back')
@login_required
def back():
    temp_causes = Causes.query.all()
    return render_template("home.html", user=current_user, causes=temp_causes)

@auth.route('/view_profile')
@login_required
def view():
    return render_template("profile.html", user=current_user)

@auth.route('/update', methods=['GET', 'POST'])
@login_required
def update():
    if request.method == 'POST':
        new_firstname = request.form.get('firstname')
        new_lastname = request.form.get('lastname')
        new_username = request.form.get('username')
        old_password = request.form.get('password_old')
        new_pass_1 = request.form.get('password_new1')
        new_pass_2 = request.form.get('password_new2')
        new_country = request.form.get('country')
        new_email = request.form.get('email')
        mod_user = User.query.filter_by(username=current_user.username).first()
        if new_firstname != mod_user.firstname and new_firstname != '':
            mod_user.firstname = new_firstname
            flash('Changed First Name!', category='success')
            db.session.commit()
        if new_lastname != mod_user.lastname and new_lastname != '':
            mod_user.lastname = new_lastname
            flash('Changed Last Name!', category='success')
            db.session.commit()
        if new_username != mod_user.username and new_username != '':
            mod_user.username = new_username
            flash('Changed UserName!', category='success')
            db.session.commit()
        if new_country != mod_user.country and new_country != '':
            mod_user.country = new_country
            flash('Changed Country!', category='success')
            db.session.commit()
        if new_email != mod_user.email and new_email != '':
            mod_user.email = new_email
            flash('Changed Email!', category='success')
            db.session.commit()
        if old_password != '':
            if check_password_hash(mod_user.password, old_password):
                if ((new_pass_1 != '') and (new_pass_1 == new_pass_2)):
                    mod_user.password = generate_password_hash(new_pass_1)
                    flash("Password changed sucessfully!", category='success')
                    db.session.commit()
                else:
                    flash("You failed to verify your new password!", category='error')
            else:
                flash('Wrong password!', category='error')
    return render_template("profile.html", user=current_user)



@auth.route('/successful_payment', methods=['GET', 'POST'])
@login_required
def payment():
    id = request.form.get('number')
    paid_cause = Causes.query.filter_by(id=id).first()
    amount = request.form.get('amount')
    if amount == '':
        selected = request.form.get('payment')
        selected = int(selected)
        paid_cause.donated_amount += selected
        paid_cause.remaining_amount -= selected
    else:
        print(amount)
        amount = int(amount)
        paid_cause.donated_amount += amount
        paid_cause.remaining_amount -= amount
    db.session.commit()
    temp_causes = Causes.query.all()
    return render_template("home.html", user=current_user, causes=temp_causes)

@auth.route('/create_cause', methods=['GET', 'POST'])
def create_cause():
    if request.method == 'POST':
        new_title = request.form.get('cause_name')
        picture = "none"
        new_description = request.form.get('description')
        new_donated_amount = 0
        new_remaining_amount = request.form.get('amount')
        print(new_remaining_amount)
        new_remaining_amount = int(new_remaining_amount)
        if len(new_description) < 20:
            flash("Please write a longer description!", category='error')
        elif new_remaining_amount < 100:
            flash("Minimum amount too low!", category='error')
        else:
            f = request.files['file']
            f.save(f'website\static\images\{secure_filename(f.filename)}')
            picture=f'static/images/{secure_filename(f.filename)}'
            new_cause = Causes(title=new_title, picture=picture, description=new_description, donated_amount=new_donated_amount, remaining_amount=new_remaining_amount)
            db.session.add(new_cause)
            db.session.commit()
            flash('Cause Created', category='success')
            return render_template("login.html", user=current_user)
        


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('name')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                temp_causes = Causes.query.all()
                if user.is_admin == 0:
                    return render_template("home.html", user=current_user, causes=temp_causes)
                else:
                    return render_template("createCause.html", user=current_user)
            else:
                flash('Incorrect password', category='error')
        else:
            flash('Email does not exist', category='error')

    return render_template("login.html", user=current_user)

@auth.route('/redirect', methods=['GET', 'POST'])
@login_required
def redirect():
    if request.method == "POST":
        number = request.form.get('number')
        temp_cause = Causes.query.filter_by(id=number).first()
        return render_template("card.html", user=current_user, temp_cause=temp_cause)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auths.login'))

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        firstname = request.form.get('firstname')
        lastname = request.form.get('lastname')
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')
        country = request.form.get('country')
        if request.form.get('is_admin'):
            is_admin = 1
        else:
            is_admin = 0
        user = User.query.filter_by(username=username).first()
        if user:
            flash('Username already exists', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 3 characters', category='error')
        elif len(password) < 7:
            flash('Password must be at least 7 characters', category='error')
        else:
            new_user = User(firstname=firstname, lastname=lastname, username=username, password=generate_password_hash(password), email=email, country=country, is_admin=is_admin)
            db.session.add(new_user)
            db.session.commit()
            #login_user(user, remember=True)
            flash('Account created', category='success')
            return render_template("login.html")
        
    return render_template("register.html", user=current_user)