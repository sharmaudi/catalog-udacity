from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Length


class ItemForm(FlaskForm):
    name = StringField('Item Name', [DataRequired(), Length(1, 255)])
    description = TextAreaField('Description', [DataRequired()], render_kw={"rows": 10, "cols": 11})
    category_id = SelectField('Category', [DataRequired()], coerce=int)


class UploadForm(FlaskForm):
    image = FileField('Upload Image', validators=[
        FileRequired(),
        FileAllowed(['jpg', 'png'], 'Images only!')
    ])
