from flask import Blueprint, render_template, request, redirect, url_for, flash, session

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# Dummy user database
users = {
    "testuser": "testpass",
    "admin": "admin123"
}

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username in users and users[username] == password:
            session['user'] = username
            flash('Logged in successfully!', 'success')
            return redirect(url_for('main.home'))  # Assuming you have home route in main
        else:
            flash('Invalid username or password', 'danger')
            return redirect(url_for('auth.login'))

    return render_template('login.html')
