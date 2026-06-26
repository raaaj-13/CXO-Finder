from flask import Flask
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config.config import SECRET_KEY
from routes.routes import main
from models.database import init_db

def create_app():
    app = Flask(__name__,
                template_folder='templates',
                static_folder='static')
    
    app.config['SECRET_KEY'] = SECRET_KEY
    
    # Initialize database
    init_db()
    
    # Register blueprint
    app.register_blueprint(main)
    
    return app

app = create_app()

if __name__ == '__main__':
    print("\n=============================")
    print("  CXO Finder App Starting...")
    print("  Visit: http://127.0.0.1:5000")
    print("=============================\n")
    app.run(debug=True, port=5000)
