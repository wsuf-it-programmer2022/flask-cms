from flask import Flask
from os import environ, path, mkdir
from python_cms.db import db
from flask_login import LoginManager

from python_cms.blueprints.pages import pages_blueprint
from python_cms.blueprints.auth import auth_blueprint

from python_cms.models.user import UserModel
from python_cms.models.post import PostModel
from flask_ckeditor import CKEditor

app = Flask(__name__)

app.register_blueprint(pages_blueprint)
app.register_blueprint(auth_blueprint)

ROOT_PATH = app.root_path

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# this is a route that will be used by ckeditor to upload files
app.config['CKEDITOR_FILE_UPLOADER'] = 'pages.upload'
db.init_app(app)
ckeditor = CKEditor(app)

# when jijna2 template is changed, app will be reloaded automatically
app.jinja_env.auto_reload = True
app.secret_key = environ.get('SECRET_KEY')
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
  return UserModel.get(user_id)


@login_manager.unauthorized_handler
def unauthorized():
  return "You must be logged in to view this page.", 403


with app.app_context():
  db.create_all()
  files_path = path.join(ROOT_PATH, 'files_upload')
  if not path.exists(files_path):
    mkdir(files_path)
