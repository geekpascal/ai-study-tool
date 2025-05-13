from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, PasswordField, SelectField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional
from email_validator import validate_email, EmailNotValidError

class ProfileForm(FlaskForm):
    """Form for editing user profile."""
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    time_zone = SelectField('Time Zone', choices=[
        ('UTC', 'UTC'),
        ('US/Eastern', 'US/Eastern'),
        ('US/Central', 'US/Central'),
        ('US/Mountain', 'US/Mountain'),
        ('US/Pacific', 'US/Pacific'),
        ('Europe/London', 'Europe/London'),
        ('Europe/Paris', 'Europe/Paris'),
        ('Asia/Tokyo', 'Asia/Tokyo'),
        ('Australia/Sydney', 'Australia/Sydney')
    ])
    study_goal = StringField('Study Goal', validators=[Optional(), Length(max=200)])
    bio = StringField('Bio', validators=[Optional(), Length(max=500)])
    submit = SubmitField('Update Profile')

class PasswordChangeForm(FlaskForm):
    """Form for changing user password."""
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[
        DataRequired(),
        Length(min=8, message='Password must be at least 8 characters')
    ])
    confirm_password = PasswordField('Confirm New Password', validators=[
        DataRequired(),
        EqualTo('new_password', message='Passwords must match')
    ])
    submit = SubmitField('Change Password') 