from flask import Flask

from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate
from flask_mail import Mail,Message



csrf=CSRFProtect()
mail = Mail()

def create_app():
   
   from main.models import db
   app = Flask(__name__,instance_relative_config=True)
   
   app.config.from_pyfile("config.py",silent=True)
   db.init_app(app)
   migrate = Migrate(app,db)
   csrf.init_app(app)
   mail.init_app(app)
   return app

app = create_app()

#Loading the routes
from main import admin_route,user_route
from main.forms import *