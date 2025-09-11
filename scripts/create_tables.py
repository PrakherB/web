from flask import Flask
from src.database.models import db
from config.database import DatabaseConfig

def create_tables():
    print("Creating database tables...")
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = DatabaseConfig.get_database_uri()
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    with app.app_context():
        db.create_all()
    print("Tables created successfully.")

if __name__ == "__main__":
    create_tables()
