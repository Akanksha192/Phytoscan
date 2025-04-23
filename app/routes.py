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
