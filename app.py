from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.secret_key = 'thesecretkey' 

from flask import session, redirect, url_for, flash

@app.route('/')
def func():
     return render_template('index.html')

@app.route('/home')
def home():
    return render_template('index.html')

@app.route('/education')
def education():
    return render_template('education.html')

@app.route('/scan')
def scan():
    return render_template('scan.html')

@app.route('/rewards')
def rewards():
    if 'username' not in session:
        flash('Please log in to access this page.', 'warning')
        return redirect(url_for('login'))
    return render_template('rewards.html')

@app.route('/about')
def about():
    return render_template('about.html')

from flask import jsonify
    
if __name__ == '__main__':
    app.run(debug=True)