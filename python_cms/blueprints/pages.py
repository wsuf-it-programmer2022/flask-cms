from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from python_cms.forms.post_form import PostForm

pages_blueprint = Blueprint('pages', __name__)


@pages_blueprint.route('/')
def index():
  return render_template('index.html.j2')


@pages_blueprint.route('/about')
def about():
  return render_template('about.html.j2')


@pages_blueprint.route('/add')
@login_required
def create_post():
  form = PostForm()
  return render_template('create_post.html.j2', form=form)
