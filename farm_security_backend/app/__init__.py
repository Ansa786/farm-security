# app/__init__.py
import os
from flask import Flask

# Attempt to import Flask-SQLAlchemy and provide a clear error if missing
try:
    from flask_sqlalchemy import SQLAlchemy
except ModuleNotFoundError:
    import sys
    sys.exit(
        "Missing dependency 'Flask-SQLAlchemy'. Install it and retry.\n\n"
        "  pip install Flask-SQLAlchemy\n\n"
        "If you have a requirements file, you can also run:\n\n"
        "  pip install -r requirements.txt\n"
    )

# create the db instance here so models can import "from app import db"
db = SQLAlchemy()

def create_app(db_url=None):
    # Flask App Factory
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default_secret')
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url or os.getenv('DATABASE_URL', 'sqlite:///events.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize Extensions
    db.init_app(app)

    # Register Blueprints (Routes)
    from app.routes.system import system_bp
    from app.routes.events import events_bp
    
    app.register_blueprint(system_bp)
    app.register_blueprint(events_bp)
    
    # Simple root route for dashboard rendering
    @app.route('/')
    def index():
        from flask import render_template
        return render_template('index.html')

    # import models after db is created to avoid circular imports
    with app.app_context():
        from app.models import event  # registers the model(s)
        # Create all tables from models
        db.create_all()
        print("✅ Database tables created/verified")

    return app

# allow running with `python -m app`
if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000)