from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models.skill import Skill
from app.forms.skill import SkillForm, SkillProgressForm
from datetime import datetime
import json

skills_bp = Blueprint('skills', __name__, url_prefix='/skills')

@skills_bp.route('/')
@login_required
def index():
    skills = Skill.query.filter_by(user_id=current_user.id).all()
    return render_template('skills/index.html', skills=skills)

@skills_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    form = SkillForm()
    if form.validate_on_submit():
        # Handle resources as JSON
        resources = []
        for i in range(len(form.resource_links.data)):
            if form.resource_links.data[i] and form.resource_descriptions.data[i]:
                resources.append({
                    'link': form.resource_links.data[i],
                    'description': form.resource_descriptions.data[i]
                })
        
        skill = Skill(
            name=form.name.data,
            description=form.description.data,
            category=form.category.data,
            proficiency_level=form.proficiency_level.data,
            target_level=form.target_level.data,
            resources=json.dumps(resources),
            user_id=current_user.id
        )
        
        db.session.add(skill)
        db.session.commit()
        flash('Skill added successfully!', 'success')
        return redirect(url_for('skills.index'))
    
    return render_template('skills/create.html', form=form)

@skills_bp.route('/<int:id>')
@login_required
def show(id):
    skill = Skill.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    resources = json.loads(skill.resources) if skill.resources else []
    return render_template('skills/show.html', skill=skill, resources=resources)

@skills_bp.route('/<int:id>/progress', methods=['GET', 'POST'])
@login_required
def update_progress(id):
    skill = Skill.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    form = SkillProgressForm(obj=skill)
    
    if form.validate_on_submit():
        skill.proficiency_level = form.proficiency_level.data
        skill.last_practiced = datetime.utcnow()
        db.session.commit()
        flash('Progress updated!', 'success')
        return redirect(url_for('skills.show', id=skill.id))
    
    return render_template('skills/progress.html', form=form, skill=skill)

@skills_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    skill = Skill.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    db.session.delete(skill)
    db.session.commit()
    flash('Skill deleted successfully!', 'success')
    return redirect(url_for('skills.index')) 