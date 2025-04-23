from flask import Blueprint, render_template, redirect, url_for, request, flash
from .models import User
from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    # Implement login logic here
    return render_template('login.html')

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    # Implement signup logic here
    return render_template('register.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))
