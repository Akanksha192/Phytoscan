from flask import Flask
from .models import db, bcrypt

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your_secret_key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
    db.init_app(app)
    bcrypt.init_app(app)

    from .routes.auth import auth_bp
    app.register_blueprint(auth_bp)

    return app
