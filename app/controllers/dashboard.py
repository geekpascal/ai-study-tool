from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.models.schedule import Schedule, ScheduleItem
from app.models.material import Material
from app.models.skill import Skill
from datetime import datetime, timedelta

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@dashboard_bp.route('/dashboard')
@login_required
def index():
    # Get today's schedule
    today = datetime.utcnow().date()
    date_schedule = Schedule.query.filter_by(
        user_id=current_user.id, 
        date=today
    ).first()
    
    # Also get the most recent schedule if date-based schedule not found
    recent_schedule = None
    if not date_schedule:
        recent_schedule = Schedule.query.filter_by(
            user_id=current_user.id
        ).order_by(Schedule.created_at.desc()).first()
    
    # Use whichever schedule is available
    schedule = date_schedule or recent_schedule
    
    # Get schedule items if schedule exists
    schedule_items = []
    if schedule:
        # Check if schedule has date attribute (for daily schedules)
        schedule_date = getattr(schedule, 'date', today)
        schedule_items = schedule.items.all() if hasattr(schedule, 'items') else []
    
    # Get upcoming deadlines (materials due in the next 7 days)
    upcoming_deadline = datetime.utcnow() + timedelta(days=7)
    upcoming_materials = Material.query.filter(
        Material.user_id == current_user.id,
        Material.deadline <= upcoming_deadline,
        Material.deadline >= datetime.utcnow()
    ).order_by(Material.deadline).limit(5).all()
    
    # Get skills not practiced recently (more than 3 days)
    three_days_ago = datetime.utcnow() - timedelta(days=3)
    neglected_skills = Skill.query.filter(
        Skill.user_id == current_user.id,
        (Skill.last_practiced <= three_days_ago) | (Skill.last_practiced == None)
    ).order_by(Skill.last_practiced).limit(5).all()
    
    # Get materials and skills with low progress
    low_progress_materials = Material.query.filter_by(user_id=current_user.id).all()
    low_progress_materials = [m for m in low_progress_materials if m.progress_percentage() < 30]
    
    low_progress_skills = Skill.query.filter_by(user_id=current_user.id).all()
    low_progress_skills = [s for s in low_progress_skills if s.progress_percentage() < 30]
    
    return render_template(
        'dashboard/index.html',
        schedule=schedule,
        schedule_items=schedule_items,
        upcoming_materials=upcoming_materials,
        neglected_skills=neglected_skills,
        low_progress_materials=low_progress_materials,
        low_progress_skills=low_progress_skills
    ) 