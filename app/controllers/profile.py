from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models.user import User
from app.forms.profile import ProfileForm, PasswordChangeForm
import os

profile_bp = Blueprint('profile', __name__, url_prefix='/profile')

@profile_bp.route('/', methods=['GET'])
@login_required
def view():
    """View user profile."""
    return render_template('profile/view.html', user=current_user)

@profile_bp.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    """Edit user profile."""
    form = ProfileForm(obj=current_user)
    
    if form.validate_on_submit():
        form.populate_obj(current_user)
        db.session.commit()
        flash('Your profile has been updated successfully!', 'success')
        return redirect(url_for('profile.view'))
    
    return render_template('profile/edit.html', form=form)

@profile_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Change user password."""
    form = PasswordChangeForm()
    
    if form.validate_on_submit():
        if current_user.check_password(form.current_password.data):
            current_user.set_password(form.new_password.data)
            db.session.commit()
            flash('Your password has been changed successfully!', 'success')
            return redirect(url_for('profile.view'))
        else:
            flash('Current password is incorrect.', 'danger')
    
    return render_template('profile/change_password.html', form=form)

@profile_bp.route('/dashboard-stats', methods=['GET'])
@login_required
def dashboard_stats():
    """Get user dashboard statistics."""
    total_materials = len(current_user.materials)
    total_skills = len(current_user.skills)
    total_schedules = len(current_user.schedules)
    
    # Calculate progress stats
    materials_completed = sum(1 for material in current_user.materials if material.progress_percentage() == 100)
    skills_completed = sum(1 for skill in current_user.skills if skill.proficiency_level >= skill.target_level)
    
    schedule_stats = {
        'active': sum(1 for schedule in current_user.schedules if schedule.is_active),
        'inactive': sum(1 for schedule in current_user.schedules if not schedule.is_active),
    }
    
    stats = {
        'materials': {
            'total': total_materials,
            'completed': materials_completed,
            'in_progress': total_materials - materials_completed
        },
        'skills': {
            'total': total_skills,
            'completed': skills_completed,
            'in_progress': total_skills - skills_completed
        },
        'schedules': {
            'total': total_schedules,
            'active': schedule_stats['active'],
            'inactive': schedule_stats['inactive']
        }
    }
    
    return render_template('profile/dashboard_stats.html', stats=stats) 