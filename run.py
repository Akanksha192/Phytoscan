from flask import Flask, jsonify, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_restful import Api, Resource

# Initialize the app and set up configurations
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
api = Api(app)  # Set up Flask-RESTful API

# User model for the database
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

# Load the user (flask-login)
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Home route
@app.route('/')
def index():
    return 'Home Page'

# API: Login route (POST request)
class LoginAPI(Resource):
    def post(self):
        data = request.get_json()  # Get JSON data from the request
        username = data.get('username')
        password = data.get('password')

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            return jsonify({"message": "Login successful", "username": user.username}), 200
        else:
            return jsonify({"message": "Invalid username or password"}), 401  # Unauthorized

# API: Logout route (POST request)
class LogoutAPI(Resource):
    def post(self):
        logout_user()
        return jsonify({"message": "Logout successful"}), 200

# Add API resources to the API endpoint
api.add_resource(LoginAPI, '/api/login')
api.add_resource(LogoutAPI, '/api/logout')

# Sign Up route (For creating new users)
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if User.query.filter_by(username=username).first():
            flash("User already exists!")
            return redirect(url_for('signup'))
        
        hashed_password = generate_password_hash(password, method='sha256')
        
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash("Sign-up successful! You can now log in.")
        return redirect(url_for('login'))
    
    return render_template('signup.html')

# Login route (Web-based, not the API)
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash("User does not exist or incorrect password!")
            return redirect(url_for('login'))

    return render_template('login.html')

# Dashboard route (protected)
@app.route('/dashboard')
@login_required
def dashboard():
    return f"Welcome, {current_user.username}!"

# Logout route (Web-based, not the API)
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

if __name__ == '__main__':
    db.create_all()  # Create the database tables if they don't exist
    app.run(debug=True)
