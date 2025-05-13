from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, IntegerField, SubmitField, FieldList
from wtforms.validators import DataRequired, Optional, NumberRange, URL

class SkillForm(FlaskForm):
    name = StringField('Skill Name', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[Optional()])
    category = SelectField('Category', choices=[
        ('programming', 'Programming'),
        ('design', 'Design'),
        ('language', 'Language'),
        ('math', 'Mathematics'),
        ('science', 'Science'),
        ('business', 'Business'),
        ('other', 'Other')
    ])
    proficiency_level = IntegerField('Current Level (1-10)', validators=[
        DataRequired(), NumberRange(min=1, max=10)
    ])
    target_level = IntegerField('Target Level (1-10)', validators=[
        DataRequired(), NumberRange(min=1, max=10)
    ])
    resource_links = FieldList(
        StringField('Resource Link', validators=[Optional(), URL()]),
        min_entries=3
    )
    resource_descriptions = FieldList(
        StringField('Resource Description', validators=[Optional()]),
        min_entries=3
    )
    submit = SubmitField('Add Skill')

class SkillProgressForm(FlaskForm):
    proficiency_level = IntegerField('Current Level (1-10)', validators=[
        DataRequired(), NumberRange(min=1, max=10)
    ])
    submit = SubmitField('Update Progress') 