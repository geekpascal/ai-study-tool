from app import db
from app.models.schedule import Schedule, ScheduleItem
from app.models.material import Material
from app.models.skill import Skill
from datetime import datetime, timedelta, time
import json

def generate_daily_schedule(user_id, target_date):
    """
    Generate a daily schedule for the user
    Automatically allocates time for studying materials and practicing skills
    """
    # Check if user has materials and skills
    materials = Material.query.filter_by(user_id=user_id).all()
    skills = Skill.query.filter_by(user_id=user_id).all()
    
    if not materials and not skills:
        return None
    
    # Create a new schedule
    schedule = Schedule(user_id=user_id, date=target_date)
    db.session.add(schedule)
    db.session.commit()
    
    # Time slots
    # Morning academic session (9 AM - 12 PM)
    morning_start = time(9, 0)
    morning_end = time(12, 0)
    
    # Afternoon skill session (1 PM - 3 PM)
    afternoon_start = time(13, 0)
    afternoon_end = time(15, 0)
    
    # Evening review academic (5 PM - 6 PM)
    evening_academic_start = time(17, 0)
    evening_academic_end = time(18, 0)
    
    # Evening review skill (9 PM - 11 PM)
    evening_skill_start = time(21, 0)
    evening_skill_end = time(23, 0)
    
    # Prioritize materials with upcoming deadlines
    priority_materials = sorted(
        [m for m in materials if m.deadline and m.progress_percentage() < 100],
        key=lambda x: x.deadline
    )
    
    # Prioritize skills not practiced recently
    priority_skills = sorted(
        skills,
        key=lambda x: x.days_since_last_practice() if x.days_since_last_practice() else float('inf'),
        reverse=True
    )
    
    # Create morning academic session
    if priority_materials:
        material = priority_materials[0]
        pages_to_study = material.pages_per_day()
        start_page = material.current_page + 1
        end_page = min(material.current_page + pages_to_study, material.total_pages)
        
        morning_item = ScheduleItem(
            start_time=morning_start,
            end_time=morning_end,
            item_type='academic',
            title=material.title,
            description=f"Study Pages {start_page}-{end_page}",
            material_id=material.id,
            schedule_id=schedule.id
        )
        db.session.add(morning_item)
    
    # Create afternoon skill session
    if priority_skills:
        skill = priority_skills[0]
        
        # Get resources if available
        resource_text = ""
        try:
            if skill.resources:
                resources = json.loads(skill.resources)
                if resources and len(resources) > 0:
                    resource = resources[0]
                    resource_text = f"Resource: {resource['description']} - {resource['link']}"
        except:
            pass
        
        afternoon_item = ScheduleItem(
            start_time=afternoon_start,
            end_time=afternoon_end,
            item_type='skill',
            title=skill.name,
            description=f"Practice {skill.category}: {skill.name}. {resource_text}",
            skill_id=skill.id,
            schedule_id=schedule.id
        )
        db.session.add(afternoon_item)
    
    # Create evening academic review
    if priority_materials:
        material = priority_materials[0]
        
        evening_academic_item = ScheduleItem(
            start_time=evening_academic_start,
            end_time=evening_academic_end,
            item_type='academic',
            title=f"Review: {material.title}",
            description=f"Review your morning study of {material.title}",
            material_id=material.id,
            schedule_id=schedule.id
        )
        db.session.add(evening_academic_item)
    
    # Create evening skill review
    if priority_skills:
        skill = priority_skills[0]
        
        evening_skill_item = ScheduleItem(
            start_time=evening_skill_start,
            end_time=evening_skill_end,
            item_type='skill',
            title=f"Review: {skill.name}",
            description=f"Review what you learned about {skill.name} today",
            skill_id=skill.id,
            schedule_id=schedule.id
        )
        db.session.add(evening_skill_item)
    
    db.session.commit()
    return schedule 