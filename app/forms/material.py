from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, DateField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Optional, NumberRange

class MaterialForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[Optional()])
    file = FileField('PDF File', validators=[
        Optional(),
        FileAllowed(['pdf'], 'PDFs only!')
    ])
    total_pages = IntegerField('Total Pages', validators=[Optional(), NumberRange(min=1)])
    deadline = DateField('Deadline', format='%Y-%m-%d', validators=[Optional()])
    submit = SubmitField('Add Material')

class MaterialProgressForm(FlaskForm):
    current_page = IntegerField('Current Page', validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField('Update Progress') 