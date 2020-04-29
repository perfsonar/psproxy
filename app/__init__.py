from flask import Flask
from flask_cors import CORS
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

origin = app.config['APPURL']
cors = CORS(app, resources={r"/api/*": {"origins": origin}})

from app import routes

