from flask import Blueprint, render_template, request, redirect, url_for, flash, send_from_directory
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from python_cms.forms.post_form import PostForm
import python_cms
from os import path
from bs4 import BeautifulSoup
from flask_ckeditor import upload_success, upload_fail

from python_cms.models.post import PostModel

pages_blueprint = Blueprint('pages', __name__)

VALID_TAGS = [
    'div', 'br', 'p', 'h1', 'h2', 'img', 'h3', 'ul', 'li', 'em', 'strong', 'a',
    'blockquote'
]


def sanitize_html(value):
  soup = BeautifulSoup(value, features="html.parser")
  for tag in soup.findAll(True):
    if tag.name not in VALID_TAGS:
      tag.extract()

  return soup.renderContents()


@pages_blueprint.route('/')
def index():
  posts = PostModel.get_all()
  for post in posts:
    if type(post.body) == bytes:
      post.body = post.body.decode('utf-8')
    if type(post.title) == bytes:
      post.title = post.title.decode('utf-8')
  return render_template('index.html.j2', posts=posts)


@pages_blueprint.route('/files/<path:filename>')
def files(filename):
  directory = path.join(python_cms.ROOT_PATH, 'files_upload')
  return send_from_directory(directory=directory, path=filename)


@pages_blueprint.route('/post/<int:post_id>')
def post(post_id):
  post = PostModel.get(post_id)
  post.body = post.body.decode('utf-8')
  post.title = post.title.decode('utf-8')
  if not post:
    return "post not found", 404
  return render_template('post.html.j2', post=post)


@pages_blueprint.route('/about')
def about():
  return render_template('about.html.j2')


@pages_blueprint.route('/add', methods=['GET', 'POST'])
@login_required
def create_post():
  form = PostForm()
  if request.method == 'POST' and form.validate_on_submit():
    title = request.form['title']
    body = request.form['body']
    user = current_user.get_id()
    clean_title = sanitize_html(title)
    clean_body = sanitize_html(body)

    file = request.files['teaser_image']
    print(file)
    filename = secure_filename(file.filename)
    file.save(path.join(python_cms.ROOT_PATH, 'files_upload', filename))

    post = PostModel(title=clean_title,
                     body=clean_body,
                     user_id=user,
                     teaser_image=filename)
    post.save()
    flash(f'Post {title} created successfully', 'success')
    print(request.form)
    return redirect(url_for('pages.create_post'))
  print(form.errors)

  return render_template('create_post.html.j2', form=form)


@pages_blueprint.route('/upload', methods=['POST'])
def upload():
  f = request.files['upload']
  extension = f.filename.split('.')[-1].lower()
  if extension not in ['jpg', 'gif', 'png', 'jpeg']:
    return upload_fail(message="File extension not allowed")
  directory = path.join(python_cms.ROOT_PATH, 'files_upload')
  filename = secure_filename(f.filename)
  f.save(path.join(directory, filename))
  url = url_for('pages.files', filename=filename)

  return upload_success(url=url, filename=filename)
