from flask import Flask
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__,
            static_url_path='',
            static_folder='../static',
            template_folder='../templates')

app.config.from_object('config.DevelopmentConfig')
db = SQLAlchemy(app)

from .routes import routes
app.register_blueprint(routes, url_prefix='/')
