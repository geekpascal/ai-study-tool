from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models.material import Material
from app.models.skill import Skill
from app.models.schedule import Schedule, ScheduleItem
from app.services.gemini_service import (
    check_api_key as check_gemini_key,
    analyze_material,
    analyze_skill_progress,
    generate_optimized_schedule,
    generate_study_insights,
    get_gemini_recommendations
)
from app.services.tavily_service import (
    check_api_key as check_tavily_key,
    search_learning_resources,
    search_practice_exercises,
    enrich_material_with_web_data
)
import json

ai_bp = Blueprint('ai', __name__, url_prefix='/ai')

@ai_bp.route('/status')
@login_required
def status():
    """Check AI services status"""
    gemini_status = check_gemini_key()
    tavily_status = check_tavily_key()
    
    return jsonify({
        'gemini_api': 'active' if gemini_status else 'inactive',
        'tavily_api': 'active' if tavily_status else 'inactive',
        'message': 'AI services are ready' if gemini_status and tavily_status else 'Some AI services are inactive'
    })

@ai_bp.route('/analyze/material/<int:material_id>')
@login_required
def analyze_material_route(material_id):
    """Analyze a study material and provide insights"""
    material = Material.query.filter_by(id=material_id, user_id=current_user.id).first_or_404()
    
    # Get current progress
    progress = material.current_page if hasattr(material, 'current_page') else None
    
    # Get analysis from Gemini
    analysis = analyze_material(material, progress)
    
    # Get web resources from Tavily
    web_data = enrich_material_with_web_data(material.title, material.description)
    
    return render_template(
        'ai/material_analysis.html',
        material=material,
        analysis=analysis,
        web_data=web_data
    )

@ai_bp.route('/analyze/skill/<int:skill_id>')
@login_required
def analyze_skill_route(skill_id):
    """Analyze a skill and provide learning path"""
    skill = Skill.query.filter_by(id=skill_id, user_id=current_user.id).first_or_404()
    
    # Get analysis from Gemini
    analysis = analyze_skill_progress(skill)
    
    # Get practice resources from Tavily
    skill_level = "beginner"
    if skill.proficiency_level > 3 and skill.proficiency_level <= 7:
        skill_level = "intermediate"
    elif skill.proficiency_level > 7:
        skill_level = "advanced"
    
    practice_resources = search_practice_exercises(skill.name, skill_level)
    learning_resources = search_learning_resources(skill.name, skill_level)
    
    return render_template(
        'ai/skill_analysis.html',
        skill=skill,
        analysis=analysis,
        practice_resources=practice_resources,
        learning_resources=learning_resources
    )

@ai_bp.route('/generate/schedule', methods=['GET', 'POST'])
@login_required
def generate_schedule_route():
    """Generate an optimized study schedule"""
    if request.method == 'POST':
        # Get form data
        available_hours = request.form.get('available_hours', 4)
        preferences = request.form.get('preferences', '')
        
        # Get user's materials and skills
        materials = Material.query.filter_by(user_id=current_user.id).all()
        skills = Skill.query.filter_by(user_id=current_user.id).all()
        
        # Generate schedule
        schedule_data = generate_optimized_schedule(materials, skills, available_hours, preferences)
        
        return render_template(
            'ai/schedule_result.html',
            schedule=schedule_data,
            materials=materials,
            skills=skills
        )
    
    return render_template('ai/generate_schedule.html')

@ai_bp.route('/insights')
@login_required
def study_insights_route():
    """Generate personalized study insights"""
    # Collect user data
    materials = Material.query.filter_by(user_id=current_user.id).all()
    skills = Skill.query.filter_by(user_id=current_user.id).all()
    schedules = Schedule.query.filter_by(user_id=current_user.id).all()
    
    # Calculate statistics
    materials_count = len(materials)
    materials_completed = sum(1 for m in materials if hasattr(m, 'progress_percentage') and m.progress_percentage() == 100)
    
    skills_count = len(skills)
    avg_skill_progress = 0
    if skills_count > 0:
        avg_skill_progress = sum(s.progress_percentage() for s in skills if hasattr(s, 'progress_percentage')) / skills_count
    
    schedules_count = len(schedules)
    schedule_items = []
    for schedule in schedules:
        schedule_items.extend(schedule.items.all())
    
    completed_items = sum(1 for item in schedule_items if item.completed)
    schedule_completion_rate = 0
    if len(schedule_items) > 0:
        schedule_completion_rate = (completed_items / len(schedule_items)) * 100
    
    # Calculate average study session length
    avg_study_session = 0
    if len(schedule_items) > 0:
        avg_study_session = sum(item.duration_minutes() for item in schedule_items if hasattr(item, 'duration_minutes')) / len(schedule_items)
    
    user_data = {
        'materials_count': materials_count,
        'materials_completed': materials_completed,
        'skills_count': skills_count,
        'avg_skill_progress': round(avg_skill_progress, 1),
        'schedules_count': schedules_count,
        'schedule_completion_rate': round(schedule_completion_rate, 1),
        'avg_study_session': round(avg_study_session, 1)
    }
    
    # Generate insights
    insights = generate_study_insights(user_data)
    
    return render_template(
        'ai/study_insights.html',
        insights=insights,
        stats=user_data
    )

@ai_bp.route('/recommend', methods=['GET', 'POST'])
@login_required
def recommendations_route():
    """Get personalized study recommendations"""
    if request.method == 'POST':
        # Get form data
        material_id = request.form.get('material_id')
        skill_id = request.form.get('skill_id')
        
        material = None
        skill = None
        
        if material_id:
            material = Material.query.filter_by(id=material_id, user_id=current_user.id).first()
        
        if skill_id:
            skill = Skill.query.filter_by(id=skill_id, user_id=current_user.id).first()
        
        if not material or not skill:
            flash('Please select both a material and a skill', 'warning')
            return redirect(url_for('ai.recommendations_route'))
        
        # Get current progress
        progress_text = "just starting"
        if hasattr(material, 'progress_percentage'):
            progress = material.progress_percentage()
            if progress > 0:
                progress_text = f"{progress}% complete"
        
        # Get recommendations
        recommendations = get_gemini_recommendations(
            material.title, 
            skill.name,
            progress_text
        )
        
        return render_template(
            'ai/recommendations_result.html',
            recommendations=recommendations,
            material=material,
            skill=skill
        )
    
    # Get user's materials and skills for the form
    materials = Material.query.filter_by(user_id=current_user.id).all()
    skills = Skill.query.filter_by(user_id=current_user.id).all()
    
    return render_template(
        'ai/recommendations_form.html',
        materials=materials,
        skills=skills
    )

@ai_bp.route('/search', methods=['GET', 'POST'])
@login_required
def search_route():
    """Search for learning resources"""
    if request.method == 'POST':
        # Get form data
        query = request.form.get('query', '')
        resource_type = request.form.get('resource_type', '')
        skill_level = request.form.get('skill_level', 'intermediate')
        
        # Search for resources
        results = search_learning_resources(query, skill_level, resource_type)
        
        return render_template(
            'ai/search_results.html',
            results=results,
            query=query
        )
    
    return render_template('ai/search_form.html') 