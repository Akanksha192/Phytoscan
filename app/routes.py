from flask import Flask, render_template
from flask_login import login_required, current_user

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/home')
@login_required
def dashboard():
    return f"Welcome, {current_user.name}!"
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from .models import User
from . import db
from werkzeug.security import generate_password_hash, check_password_hash

auth = Blueprint('auth', __name__)

@auth.route('/')
def home():
    return render_template('login.html')

@auth.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')

    user = User.query.filter_by(email=email).first()
    if user and check_password_hash(user.password, password):
        session['user_id'] = user.id
        return redirect(url_for('auth.dashboard'))
    else:
        flash("Invalid email or password.")
        return redirect(url_for('auth.home'))

@auth.route('/dashboard')
def dashboard():
    if 'user_id' in session:
        return render_template('dashboard.html')
    else:
        return redirect(url_for('auth.home'))

@auth.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('auth.home'))

@auth.route('/signup', methods=['POST'])
def signup():
    email = request.form.get('email')
    password = request.form.get('password')
    hashed_pw = generate_password_hash(password, method='sha256')

    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        flash("Email already exists.")
        return redirect(url_for('auth.home'))

    new_user = User(email=email, password=hashed_pw)
    db.session.add(new_user)
    db.session.commit()
    flash("Account created! Please log in.")
    return redirect(url_for('auth.home'))
