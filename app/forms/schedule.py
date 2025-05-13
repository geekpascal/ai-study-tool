from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, TimeField, SubmitField, RadioField, BooleanField, DateField, SelectMultipleField, widgets
from wtforms.validators import DataRequired, Optional
from app.models.material import Material
from app.models.skill import Skill
from datetime import date
from flask_login import current_user

class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()

class ScheduleItemForm(FlaskForm):
    start_time = TimeField('Start Time', format='%H:%M', validators=[DataRequired()])
    end_time = TimeField('End Time', format='%H:%M', validators=[DataRequired()])
    item_type = RadioField('Type', choices=[
        ('academic', 'Academic Material'),
        ('skill', 'Skill Development'),
        ('other', 'Other')
    ], validators=[DataRequired()])
    material_id = SelectField('Material', coerce=int, validators=[Optional()])
    skill_id = SelectField('Skill', coerce=int, validators=[Optional()])
    title = StringField('Title (for Other items)', validators=[Optional()])
    description = TextAreaField('Description', validators=[Optional()])
    submit = SubmitField('Add to Schedule')
    
    def __init__(self, *args, **kwargs):
        super(ScheduleItemForm, self).__init__(*args, **kwargs)
        # Populate material choices
        materials = Material.query.all()
        self.material_id.choices = [(0, 'Select a Material')] + [(m.id, m.title) for m in materials]
        
        # Populate skill choices
        skills = Skill.query.all()
        self.skill_id.choices = [(0, 'Select a Skill')] + [(s.id, s.name) for s in skills]

class ScheduleForm(FlaskForm):
    title = StringField('Schedule Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[Optional()])
    start_date = DateField('Start Date', validators=[DataRequired()], default=date.today)
    end_date = DateField('End Date', validators=[DataRequired()], default=date.today)
    is_active = BooleanField('Active', default=True)
    materials = MultiCheckboxField('Materials', coerce=int, validators=[Optional()])
    skills = MultiCheckboxField('Skills', coerce=int, validators=[Optional()])
    submit = SubmitField('Create Schedule')
    
    def __init__(self, *args, **kwargs):
        super(ScheduleForm, self).__init__(*args, **kwargs)
        
        # Populate material choices with user's materials
        user_id = current_user.id if current_user.is_authenticated else None
        
        if user_id:
            materials = Material.query.filter_by(user_id=user_id).all()
            self.materials.choices = [(m.id, m.title) for m in materials]
            
            # Populate skill choices with user's skills
            skills = Skill.query.filter_by(user_id=user_id).all()
            self.skills.choices = [(s.id, s.name) for s in skills] 