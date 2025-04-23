from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = '1234567891234567891234567890000'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../users.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    from .routes import auth
    app.register_blueprint(auth)

    return app
