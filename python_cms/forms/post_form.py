from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import Length, InputRequired
from flask_wtf.file import FileField, FileAllowed


class PostForm(FlaskForm):
  title = StringField(
      'Title',
      validators=[
          InputRequired(),
          Length(min=4,
                 max=35,
                 message="Title must be between 4 and 35 characters")
      ])
  teaser_image = FileField(
      'Teaser Image',
      validators=[FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')])

  body = TextAreaField(
      'Body',
      validators=[
          InputRequired(),
          Length(min=4,
                 max=8000,
                 message="Body must be between 4 and 8000 characters")
      ])

  submit = SubmitField('Submit')
