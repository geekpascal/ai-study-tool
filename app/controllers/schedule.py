from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.schedule import Schedule, ScheduleItem
from app.models.material import Material
from app.models.skill import Skill
from app.forms.schedule import ScheduleItemForm, ScheduleForm
from app.services.schedule_service import generate_daily_schedule
from datetime import datetime, date, timedelta, time

schedule_bp = Blueprint('schedule', __name__, url_prefix='/schedule')

@schedule_bp.route('/')
@login_required
def index():
    # Get current date
    current_date = request.args.get('date')
    if current_date:
        try:
            current_date = datetime.strptime(current_date, '%Y-%m-%d').date()
        except ValueError:
            current_date = date.today()
    else:
        current_date = date.today()
    
    # Get schedule for the current date
    daily_schedule = Schedule.query.filter_by(
        user_id=current_user.id,
        date=current_date
    ).first()
    
    # Get all user schedules
    all_schedules = Schedule.query.filter_by(user_id=current_user.id).all()
    
    # Get materials and skills for forms
    materials = Material.query.filter_by(user_id=current_user.id).all()
    skills = Skill.query.filter_by(user_id=current_user.id).all()
    
    # Previous and next day links
    prev_day = current_date - timedelta(days=1)
    next_day = current_date + timedelta(days=1)
    
    return render_template(
        'schedule/index.html',
        schedule=daily_schedule,
        schedules=all_schedules,
        materials=materials,
        skills=skills,
        current_date=current_date,
        prev_day=prev_day,
        next_day=next_day
    )

@schedule_bp.route('/generate', methods=['POST'])
@login_required
def generate():
    date_str = request.form.get('date')
    try:
        target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except (ValueError, TypeError):
        target_date = date.today()
    
    # Check if schedule already exists
    existing_schedule = Schedule.query.filter_by(
        user_id=current_user.id,
        date=target_date
    ).first()
    
    if existing_schedule:
        flash('Schedule for this date already exists!', 'warning')
        return redirect(url_for('schedule.index', date=target_date.strftime('%Y-%m-%d')))
    
    # Generate schedule
    schedule = generate_daily_schedule(current_user.id, target_date)
    
    if schedule:
        flash('Schedule generated successfully!', 'success')
    else:
        flash('Failed to generate schedule. Please add materials and skills first.', 'error')
    
    return redirect(url_for('schedule.index', date=target_date.strftime('%Y-%m-%d')))

@schedule_bp.route('/item/create', methods=['POST'])
@login_required
def create_item():
    date_str = request.form.get('date')
    try:
        target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except (ValueError, TypeError):
        target_date = date.today()
    
    # Get or create schedule
    schedule = Schedule.query.filter_by(
        user_id=current_user.id,
        date=target_date
    ).first()
    
    if not schedule:
        schedule = Schedule(user_id=current_user.id, date=target_date)
        db.session.add(schedule)
        db.session.commit()
    
    form = ScheduleItemForm()
    
    if form.validate_on_submit():
        # Create schedule item
        item = ScheduleItem(
            start_time=form.start_time.data,
            end_time=form.end_time.data,
            item_type=form.item_type.data,
            title=form.title.data,
            description=form.description.data,
            schedule_id=schedule.id
        )
        
        # Link to material or skill if applicable
        if form.item_type.data == 'academic' and form.material_id.data:
            item.material_id = form.material_id.data
            material = Material.query.get(form.material_id.data)
            if material and form.material_id.data != 0:
                item.title = material.title
        elif form.item_type.data == 'skill' and form.skill_id.data:
            item.skill_id = form.skill_id.data
            skill = Skill.query.get(form.skill_id.data)
            if skill and form.skill_id.data != 0:
                item.title = skill.name
        
        db.session.add(item)
        db.session.commit()
        flash('Schedule item added!', 'success')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{getattr(form, field).label.text}: {error}", 'error')
    
    return redirect(url_for('schedule.index', date=target_date.strftime('%Y-%m-%d')))

@schedule_bp.route('/item/<int:id>/complete', methods=['POST'])
@login_required
def complete_item(id):
    item = ScheduleItem.query.get_or_404(id)
    schedule = Schedule.query.get_or_404(item.schedule_id)
    
    # Verify ownership
    if schedule.user_id != current_user.id:
        flash('Unauthorized access!', 'error')
        return redirect(url_for('schedule.index'))
    
    item.completed = True
    
    # Update material progress if applicable
    if item.material_id:
        material = Material.query.get(item.material_id)
        if material and material.user_id == current_user.id:
            # Update current page based on item description
            # This assumes description contains pages info like "Pages 10-15"
            try:
                description = item.description or ""
                if "Pages" in description:
                    pages_str = description.split("Pages")[1].strip()
                    pages = pages_str.split("-")
                    if len(pages) == 2:
                        end_page = int(pages[1])
                        material.current_page = max(material.current_page, end_page)
            except (IndexError, ValueError):
                pass
    
    # Update skill last practiced if applicable
    if item.skill_id:
        skill = Skill.query.get(item.skill_id)
        if skill and skill.user_id == current_user.id:
            skill.last_practiced = datetime.utcnow()
    
    db.session.commit()
    flash('Item marked as completed!', 'success')
    
    return redirect(url_for('schedule.index', date=schedule.date.strftime('%Y-%m-%d')))

@schedule_bp.route('/item/<int:id>/delete', methods=['POST'])
@login_required
def delete_item(id):
    item = ScheduleItem.query.get_or_404(id)
    schedule = Schedule.query.get_or_404(item.schedule_id)
    
    # Verify ownership
    if schedule.user_id != current_user.id:
        flash('Unauthorized access!', 'error')
        return redirect(url_for('schedule.index'))
    
    db.session.delete(item)
    db.session.commit()
    flash('Schedule item deleted!', 'success')
    
    return redirect(url_for('schedule.index', date=schedule.date.strftime('%Y-%m-%d')))

@schedule_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    form = ScheduleForm()
    
    # Populate form choices with user's materials and skills
    materials = Material.query.filter_by(user_id=current_user.id).all()
    form.materials.choices = [(m.id, m.title) for m in materials]
    
    skills = Skill.query.filter_by(user_id=current_user.id).all()
    form.skills.choices = [(s.id, s.name) for s in skills]
    
    # Validate form and create schedule
    if form.validate_on_submit():
        # Create new schedule
        schedule = Schedule(
            title=form.title.data,
            description=form.description.data,
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            is_active=form.is_active.data,
            user_id=current_user.id
        )
        
        # Save the schedule
        db.session.add(schedule)
        db.session.commit()
        
        # Default time slots (9 AM - 10 AM)
        default_start_time = time(9, 0)
        default_end_time = time(10, 0)
        
        # Process selected materials
        if form.materials.data:
            for material_id in form.materials.data:
                material = Material.query.get(material_id)
                if material and material.user_id == current_user.id:
                    # Create a schedule item for each material
                    item = ScheduleItem(
                        schedule_id=schedule.id,
                        start_time=default_start_time,
                        end_time=default_end_time,
                        item_type='academic',
                        title=material.title,
                        material_id=material.id,
                        description=f"Study {material.title}"
                    )
                    db.session.add(item)
        
        # Process selected skills
        if form.skills.data:
            for skill_id in form.skills.data:
                skill = Skill.query.get(skill_id)
                if skill and skill.user_id == current_user.id:
                    # Create a schedule item for each skill
                    item = ScheduleItem(
                        schedule_id=schedule.id,
                        start_time=default_start_time,
                        end_time=default_end_time,
                        item_type='skill',
                        title=skill.name,
                        skill_id=skill.id,
                        description=f"Practice {skill.name}"
                    )
                    db.session.add(item)
        
        db.session.commit()
        flash('Schedule created successfully!', 'success')
        return redirect(url_for('schedule.view', schedule_id=schedule.id))
    
    return render_template('schedule/create.html', form=form)

@schedule_bp.route('/<int:schedule_id>')
@login_required
def view(schedule_id):
    """View a specific schedule by ID"""
    schedule = Schedule.query.filter_by(id=schedule_id, user_id=current_user.id).first_or_404()
    
    return render_template(
        'schedule/view.html',
        schedule=schedule,
        current_date=schedule.get_display_date()
    )

@schedule_bp.route('/<int:schedule_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(schedule_id):
    schedule = Schedule.query.get_or_404(schedule_id)
    
    # Verify ownership
    if schedule.user_id != current_user.id:
        flash('Unauthorized access!', 'error')
        return redirect(url_for('schedule.index'))
    
    form = ScheduleForm(obj=schedule)
    
    # Populate form choices with user's materials and skills
    materials = Material.query.filter_by(user_id=current_user.id).all()
    form.materials.choices = [(m.id, m.title) for m in materials]
    
    skills = Skill.query.filter_by(user_id=current_user.id).all()
    form.skills.choices = [(s.id, s.name) for s in skills]
    
    # Set initial values for materials and skills
    if request.method == 'GET':
        form.materials.data = [item.material_id for item in schedule.items if item.material_id]
        form.skills.data = [item.skill_id for item in schedule.items if item.skill_id]
    
    if form.validate_on_submit():
        # Update schedule details
        schedule.title = form.title.data
        schedule.description = form.description.data
        schedule.start_date = form.start_date.data
        schedule.end_date = form.end_date.data
        schedule.is_active = form.is_active.data
        
        # Remove existing items
        for item in schedule.items:
            db.session.delete(item)
        
        # Default time slots (9 AM - 10 AM)
        default_start_time = time(9, 0)
        default_end_time = time(10, 0)
        
        # Process selected materials
        if form.materials.data:
            for material_id in form.materials.data:
                material = Material.query.get(material_id)
                if material and material.user_id == current_user.id:
                    # Create a schedule item for each material
                    item = ScheduleItem(
                        schedule_id=schedule.id,
                        start_time=default_start_time,
                        end_time=default_end_time,
                        item_type='academic',
                        title=material.title,
                        material_id=material.id,
                        description=f"Study {material.title}"
                    )
                    db.session.add(item)
        
        # Process selected skills
        if form.skills.data:
            for skill_id in form.skills.data:
                skill = Skill.query.get(skill_id)
                if skill and skill.user_id == current_user.id:
                    # Create a schedule item for each skill
                    item = ScheduleItem(
                        schedule_id=schedule.id,
                        start_time=default_start_time,
                        end_time=default_end_time,
                        item_type='skill',
                        title=skill.name,
                        skill_id=skill.id,
                        description=f"Practice {skill.name}"
                    )
                    db.session.add(item)
        
        db.session.commit()
        flash('Schedule updated successfully!', 'success')
        return redirect(url_for('schedule.view', schedule_id=schedule.id))
    
    return render_template('schedule/edit.html', form=form, schedule=schedule)

@schedule_bp.route('/<int:schedule_id>/delete', methods=['POST'])
@login_required
def delete(schedule_id):
    """Delete a schedule"""
    schedule = Schedule.query.filter_by(id=schedule_id, user_id=current_user.id).first_or_404()
    
    # Delete the schedule and all its items (cascade deletion should handle items)
    db.session.delete(schedule)
    db.session.commit()
    
    flash('Schedule deleted successfully!', 'success')
    return redirect(url_for('schedule.index'))

@schedule_bp.route('/<int:schedule_id>/add-item', methods=['GET', 'POST'])
@login_required
def add_item(schedule_id):
    """Add an item to an existing schedule"""
    schedule = Schedule.query.filter_by(id=schedule_id, user_id=current_user.id).first_or_404()
    
    form = ScheduleItemForm()
    
    # Populate the form with user's materials and skills
    materials = Material.query.filter_by(user_id=current_user.id).all()
    form.material_id.choices = [(0, 'Select a Material')] + [(m.id, m.title) for m in materials]
    
    skills = Skill.query.filter_by(user_id=current_user.id).all()
    form.skill_id.choices = [(0, 'Select a Skill')] + [(s.id, s.name) for s in skills]
    
    if form.validate_on_submit():
        # Create schedule item
        item = ScheduleItem(
            start_time=form.start_time.data,
            end_time=form.end_time.data,
            item_type=form.item_type.data,
            title=form.title.data,
            description=form.description.data,
            schedule_id=schedule.id
        )
        
        # Link to material or skill if applicable
        if form.item_type.data == 'academic' and form.material_id.data:
            item.material_id = form.material_id.data
            material = Material.query.get(form.material_id.data)
            if material and form.material_id.data != 0:
                item.title = material.title
        elif form.item_type.data == 'skill' and form.skill_id.data:
            item.skill_id = form.skill_id.data
            skill = Skill.query.get(form.skill_id.data)
            if skill and form.skill_id.data != 0:
                item.title = skill.name
        
        db.session.add(item)
        db.session.commit()
        flash('Schedule item added!', 'success')
        return redirect(url_for('schedule.view', schedule_id=schedule.id))
    
    return render_template('schedule/add_item.html', form=form, schedule=schedule)

@schedule_bp.route('/item/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_item(id):
    """Edit an existing schedule item"""
    item = ScheduleItem.query.get_or_404(id)
    schedule = Schedule.query.get_or_404(item.schedule_id)
    
    # Verify ownership
    if schedule.user_id != current_user.id:
        flash('Unauthorized access!', 'error')
        return redirect(url_for('schedule.index'))
    
    form = ScheduleItemForm(obj=item)
    
    # Populate the form with user's materials and skills
    materials = Material.query.filter_by(user_id=current_user.id).all()
    form.material_id.choices = [(0, 'Select a Material')] + [(m.id, m.title) for m in materials]
    
    skills = Skill.query.filter_by(user_id=current_user.id).all()
    form.skill_id.choices = [(0, 'Select a Skill')] + [(s.id, s.name) for s in skills]
    
    if form.validate_on_submit():
        # Update item details
        item.start_time = form.start_time.data
        item.end_time = form.end_time.data
        item.item_type = form.item_type.data
        item.description = form.description.data
        item.completed = form.completed.data
        
        # Reset material and skill IDs
        item.material_id = None
        item.skill_id = None
        
        # Link to material or skill if applicable
        if form.item_type.data == 'academic' and form.material_id.data:
            item.material_id = form.material_id.data
            material = Material.query.get(form.material_id.data)
            if material and form.material_id.data != 0:
                item.title = material.title
        elif form.item_type.data == 'skill' and form.skill_id.data:
            item.skill_id = form.skill_id.data
            skill = Skill.query.get(form.skill_id.data)
            if skill and form.skill_id.data != 0:
                item.title = skill.name
        else:
            item.title = form.title.data
        
        db.session.commit()
        flash('Schedule item updated!', 'success')
        return redirect(url_for('schedule.view', schedule_id=schedule.id))
    
    return render_template('schedule/edit_item.html', form=form, schedule=schedule, item=item) 