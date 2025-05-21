import os
import google.generativeai as genai
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

# Configure the Gemini API
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    print("Warning: GEMINI_API_KEY not found in environment variables")

def get_gemini_model():
    """Get the Gemini model"""
    try:
        return genai.GenerativeModel('gemini-2.0-flash')
    except Exception as e:
        print(f"Error loading Gemini model: {e}")
        return None

def check_api_key():
    """Check if Gemini API key is set and valid"""
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("GEMINI_API_KEY not set in .env file")
        return False
    
    # Configure the library
    try:
        genai.configure(api_key=api_key)
        # Test with a simple generation
        model = get_gemini_model()
        if not model:
            return False
        
        response = model.generate_content("Hello")
        return True
    except Exception as e:
        print(f"Error checking Gemini API key: {e}")
        return False

def get_gemini_recommendations(study_material, skill_name, current_progress):
    """
    Get personalized recommendations using Gemini API
    
    Parameters:
    - study_material: The title/description of the academic material
    - skill_name: The name of the skill being developed
    - current_progress: A description of current progress (e.g. "50% complete")
    
    Returns:
    - Dictionary containing academic_tips, skill_resources, and study_plan
    """
    if not GEMINI_API_KEY:
        return {
            "academic_tips": ["Enable Gemini API with your API key for personalized recommendations."],
            "skill_resources": ["https://example.com/placeholder"],
            "study_plan": "Add your Gemini API key to the .env file to get AI-powered recommendations."
        }
    
    model = get_gemini_model()
    if not model:
        return {
            "academic_tips": ["Error connecting to Gemini API."],
            "skill_resources": ["https://example.com/placeholder"],
            "study_plan": "Check your API key and internet connection."
        }
    
    # Create prompt for academic tips
    academic_prompt = f"""
    I'm studying {study_material} and I'm currently {current_progress} through the material.
    Can you provide 3 specific tips to improve my understanding of this subject?
    Format as a bulleted list with proper HTML formatting. Use <strong> for emphasis and <ul> and <li> tags.
    """
    
    # Create prompt for skill resources
    skill_prompt = f"""
    I'm learning {skill_name} and I'm looking for quality learning resources.
    Can you recommend 3 specific online resources (tutorials, courses, documentation) to help me improve?
    Format each resource as an HTML link (<a href="URL">Title</a>), one per line.
    """
    
    # Create prompt for study plan improvement
    plan_prompt = f"""
    I'm balancing studying {study_material} with developing {skill_name} skills.
    Can you give me a specific, actionable suggestion on how to better integrate these two areas of learning?
    Keep it under 100 words and use proper HTML formatting with <p>, <strong>, and <em> tags as appropriate.
    """
    
    try:
        # Get academic tips
        academic_response = model.generate_content(academic_prompt)
        academic_text = academic_response.text.strip()
        
        # Process academic_tips - extract from HTML if needed or convert markdown-style to HTML
        if '<ul>' in academic_text and '</ul>' in academic_text:
            academic_tips = academic_text
        else:
            # Convert markdown-style asterisks to HTML
            lines = academic_text.split('\n')
            academic_tips = '<ul>'
            for line in lines:
                line = line.strip()
                if line:
                    # Replace markdown ** with <strong>
                    line = line.replace('**', '<strong>', 1)
                    if '**' in line:
                        line = line.replace('**', '</strong>', 1)
                    
                    # Handle bullet points
                    if line.startswith('• '):
                        line = f'<li>{line[2:]}</li>'
                    elif line.startswith('* '):
                        line = f'<li>{line[2:]}</li>'
                    elif line.startswith('- '):
                        line = f'<li>{line[2:]}</li>'
                    else:
                        line = f'<li>{line}</li>'
                    
                    academic_tips += line
            academic_tips += '</ul>'
        
        # Get skill resources
        skill_response = model.generate_content(skill_prompt)
        skill_text = skill_response.text.strip()
        
        # Process skill_resources - convert to HTML links if needed
        if '<a href' in skill_text:
            skill_resources = skill_text
        else:
            lines = skill_text.split('\n')
            skill_resources = '<ul>'
            for line in lines:
                line = line.strip()
                if line:
                    # If it's already a URL, make it a link
                    if line.startswith(('http://', 'https://')):
                        skill_resources += f'<li><a href="{line}" target="_blank">{line}</a></li>'
                    else:
                        skill_resources += f'<li>{line}</li>'
            skill_resources += '</ul>'
        
        # Get study plan advice
        plan_response = model.generate_content(plan_prompt)
        study_plan = plan_response.text.strip()
        
        # Process study_plan - convert markdown-style to HTML if needed
        if '<p>' not in study_plan:
            # Replace markdown ** with <strong>
            study_plan = study_plan.replace('**', '<strong>', 1)
            if '**' in study_plan:
                study_plan = study_plan.replace('**', '</strong>', 1)
            
            # Replace markdown * with <em>
            study_plan = study_plan.replace('*', '<em>', 1)
            if '*' in study_plan:
                study_plan = study_plan.replace('*', '</em>', 1)
            
            # Wrap in paragraph if not already
            if not study_plan.startswith('<p>'):
                study_plan = f'<p>{study_plan}</p>'
        
        return {
            "academic_tips": academic_tips,
            "skill_resources": skill_resources,
            "study_plan": study_plan
        }
        
    except Exception as e:
        print(f"Error getting Gemini recommendations: {e}")
        return {
            "academic_tips": ["Error generating recommendations."],
            "skill_resources": ["https://example.com/placeholder"],
            "study_plan": f"Error: {str(e)}"
        }

def analyze_material(material, user_progress=None):
    """
    Analyze an academic material and provide personalized insights
    
    Parameters:
    - material: The material object with title, description, etc.
    - user_progress: Current page, percentage completed, etc.
    
    Returns:
    - Dictionary with analysis and recommendations
    """
    if not check_api_key():
        return {
            "summary": "Enable Gemini API to get material analysis",
            "key_concepts": ["Add your Gemini API key to see key concepts"],
            "recommended_approach": "Configure your API key in the .env file",
            "estimated_completion": "Unknown without AI analysis"
        }
    
    model = get_gemini_model()
    
    # Get current progress info
    progress_text = ""
    if user_progress:
        if hasattr(material, 'total_pages') and material.total_pages > 0:
            percentage = int((user_progress / material.total_pages) * 100)
            progress_text = f"I'm currently on page {user_progress} of {material.total_pages} ({percentage}% complete)."
        else:
            progress_text = f"I'm approximately {user_progress}% through the material."
    
    # Extract content from the material file if available
    material_content = ""
    if material.file_path:
        try:
            import os
            from flask import current_app
            import PyPDF2
            
            full_path = os.path.join(current_app.root_path, material.file_path)
            if os.path.exists(full_path):
                if material.file_type == 'pdf':
                    with open(full_path, 'rb') as file:
                        pdf_reader = PyPDF2.PdfReader(file)
                        
                        # Limit to first 5 pages or fewer if the PDF is smaller
                        page_limit = min(5, len(pdf_reader.pages))
                        
                        for page_num in range(page_limit):
                            page = pdf_reader.pages[page_num]
                            material_content += page.extract_text() + "\n\n"
                        
                        material_content = f"Content from first {page_limit} pages of the PDF:\n{material_content}"
                else:
                    # For text-based files
                    with open(full_path, 'r', encoding='utf-8') as file:
                        # Limit to first 1000 characters
                        material_content = file.read(1000)
                        material_content = f"First 1000 characters of the file:\n{material_content}"
        except Exception as e:
            print(f"Error extracting content from {material.file_path}: {e}")
            material_content = f"Unable to extract content from the file: {str(e)}"
    
    # Create analysis prompt
    analysis_prompt = f"""
    I'm studying "{material.title}". 
    {material.description if hasattr(material, 'description') and material.description else ''}
    {progress_text}
    
    {material_content if material_content else "No file content available for analysis."}
    
    Based on the ACTUAL content and information provided about this material (not assumptions), please provide:
    1. A concrete summary of what this material covers (3-4 sentences), based only on the content provided
    2. 5 key concepts from the material that I should focus on understanding
    3. A recommended approach to studying this material effectively
    4. An estimated time to completion based on the material's complexity and length
    
    If you don't have enough information about specific aspects, acknowledge that rather than making assumptions.
    
    Format your response as JSON with these keys: "summary", "key_concepts" (as array), "recommended_approach", "estimated_completion"
    """
    
    try:
        response = model.generate_content(analysis_prompt)
        # Extract the JSON-like structure from the response
        text = response.text.strip()
        
        # Simple parsing: Extract each section
        summary = extract_section(text, "summary")
        key_concepts = extract_list_section(text, "key_concepts")
        recommended_approach = extract_section(text, "recommended_approach")
        estimated_completion = extract_section(text, "estimated_completion")
        
        return {
            "summary": summary,
            "key_concepts": key_concepts,
            "recommended_approach": recommended_approach, 
            "estimated_completion": estimated_completion
        }
    except Exception as e:
        print(f"Error analyzing material: {e}")
        return {
            "summary": "Error generating analysis",
            "key_concepts": ["Error occurred during AI processing"],
            "recommended_approach": f"Error: {str(e)}",
            "estimated_completion": "Unknown due to error"
        }

def analyze_skill_progress(skill):
    """
    Analyze a skill's progress and provide personalized learning path
    
    Parameters:
    - skill: The skill object with name, description, proficiency, etc.
    
    Returns:
    - Dictionary with analysis and recommendations
    """
    if not check_api_key():
        return {
            "current_analysis": "Enable Gemini API to get skill analysis",
            "next_steps": ["Add your Gemini API key to see recommended next steps"],
            "practice_suggestions": ["Configure your API key in the .env file"],
            "expected_milestones": ["Unknown without AI analysis"]
        }
    
    model = get_gemini_model()
    
    # Calculate days since last practice
    days_since_practice = None
    if skill.last_practiced:
        days_since_practice = (datetime.utcnow() - skill.last_practiced).days
    
    # Create analysis prompt
    progress_info = f"My current proficiency is {skill.proficiency_level} out of {skill.target_level}."
    if days_since_practice is not None:
        progress_info += f" I last practiced this skill {days_since_practice} days ago."
    
    analysis_prompt = f"""
    I'm developing skills in "{skill.name}" ({skill.category} category). 
    {skill.description if hasattr(skill, 'description') and skill.description else ''}
    {progress_info}
    
    Please provide:
    1. An analysis of my current skill level and what it likely means in terms of capabilities
    2. 3 specific next steps I should take to improve
    3. 2 practical exercises or projects I could do to practice this skill
    4. Expected milestones I should aim for to reach my target level
    
    Format your response as JSON with these keys: "current_analysis", "next_steps" (as array), "practice_suggestions" (as array), "expected_milestones" (as array)
    """
    
    try:
        response = model.generate_content(analysis_prompt)
        text = response.text.strip()
        
        current_analysis = extract_section(text, "current_analysis")
        next_steps = extract_list_section(text, "next_steps")
        practice_suggestions = extract_list_section(text, "practice_suggestions")
        expected_milestones = extract_list_section(text, "expected_milestones")
        
        return {
            "current_analysis": current_analysis,
            "next_steps": next_steps,
            "practice_suggestions": practice_suggestions,
            "expected_milestones": expected_milestones
        }
    except Exception as e:
        print(f"Error analyzing skill progress: {e}")
        return {
            "current_analysis": "Error generating analysis",
            "next_steps": ["Error occurred during AI processing"],
            "practice_suggestions": ["Error processing your skill data"],
            "expected_milestones": [f"Error: {str(e)}"]
        }

def generate_optimized_schedule(materials, skills, available_hours, user_preferences=None):
    """
    Generate an optimized study schedule based on user materials, skills and constraints
    
    Parameters:
    - materials: List of user's study materials
    - skills: List of user's skills to develop
    - available_hours: Hours available per day for studying
    - user_preferences: Optional preferences (morning/evening study, etc.)
    
    Returns:
    - Dictionary with schedule recommendations
    """
    if not check_api_key():
        return {
            "daily_plan": "Enable Gemini API to get schedule recommendations",
            "material_allocations": [],
            "skill_allocations": [],
            "optimization_notes": "Add your Gemini API key to the .env file"
        }
    
    model = get_gemini_model()
    
    # Prepare materials data
    materials_data = []
    for m in materials:
        if hasattr(m, 'title') and m.title:
            material_info = {
                "title": m.title,
                "priority": "high" if hasattr(m, 'priority') and m.priority else "medium",
                "completion": f"{m.progress_percentage()}%" if hasattr(m, 'progress_percentage') else "unknown"
            }
            if hasattr(m, 'deadline') and m.deadline:
                material_info["deadline"] = m.deadline.strftime("%Y-%m-%d")
            materials_data.append(material_info)
    
    # Prepare skills data
    skills_data = []
    for s in skills:
        if hasattr(s, 'name') and s.name:
            skill_info = {
                "name": s.name,
                "current_level": s.proficiency_level if hasattr(s, 'proficiency_level') else 1,
                "target_level": s.target_level if hasattr(s, 'target_level') else 10
            }
            skills_data.append(skill_info)
    
    # Prepare user preferences
    preferences = ""
    if user_preferences:
        preferences = f"My preferences: {user_preferences}"
    
    # Create schedule prompt
    schedule_prompt = f"""
    I need help creating an optimized study schedule.
    I have {available_hours} hours available per day for studying.
    {preferences}
    
    My study materials:
    {str(materials_data)}
    
    My skills I want to develop:
    {str(skills_data)}
    
    Please create:
    1. A daily study plan with specific time blocks for different materials and skills
    2. The optimal allocation of time for each material based on priority, completion status, and deadlines
    3. The optimal allocation of time for each skill based on current and target levels
    4. Notes on how this schedule is optimized for my situation
    
    Format your response as JSON with these keys: "daily_plan", "material_allocations" (as array), "skill_allocations" (as array), "optimization_notes"
    """
    
    try:
        response = model.generate_content(schedule_prompt)
        text = response.text.strip()
        
        daily_plan = extract_section(text, "daily_plan")
        material_allocations = extract_list_section(text, "material_allocations")
        skill_allocations = extract_list_section(text, "skill_allocations")
        optimization_notes = extract_section(text, "optimization_notes")
        
        return {
            "daily_plan": daily_plan,
            "material_allocations": material_allocations,
            "skill_allocations": skill_allocations,
            "optimization_notes": optimization_notes
        }
    except Exception as e:
        print(f"Error generating optimized schedule: {e}")
        return {
            "daily_plan": "Error generating schedule",
            "material_allocations": ["Error occurred during AI processing"],
            "skill_allocations": ["Unable to allocate skill time due to an error"],
            "optimization_notes": f"Error: {str(e)}"
        }

def generate_study_insights(user_data):
    """
    Generate personalized study insights based on user's learning data
    
    Parameters:
    - user_data: Dictionary containing user's materials, skills, schedules, etc.
    
    Returns:
    - Dictionary with personalized insights
    """
    if not check_api_key():
        return {
            "learning_patterns": "Enable Gemini API to get personalized insights",
            "improvement_areas": ["Add your Gemini API key to see areas for improvement"],
            "efficiency_tips": ["Configure your API key in the .env file"],
            "success_factors": ["Unknown without AI analysis"]
        }
    
    model = get_gemini_model()
    
    # Create insights prompt
    insights_prompt = f"""
    I want insights about my learning patterns based on my study data:
    
    Materials: {user_data.get('materials_count', 0)} total, {user_data.get('materials_completed', 0)} completed
    Skills: {user_data.get('skills_count', 0)} total, progress averages {user_data.get('avg_skill_progress', 0)}%
    Schedules: {user_data.get('schedules_count', 0)} created, completion rate {user_data.get('schedule_completion_rate', 0)}%
    Study sessions: Average {user_data.get('avg_study_session', 0)} minutes
    
    Please provide:
    1. Analysis of my learning patterns and habits
    2. 3 areas where I could improve my learning efficiency
    3. 3 personalized tips for studying more effectively
    4. Key factors that seem to contribute to my learning success
    
    Format your response as JSON with these keys: "learning_patterns", "improvement_areas" (as array), "efficiency_tips" (as array), "success_factors" (as array)
    """
    
    try:
        response = model.generate_content(insights_prompt)
        text = response.text.strip()
        
        learning_patterns = extract_section(text, "learning_patterns")
        improvement_areas = extract_list_section(text, "improvement_areas")
        efficiency_tips = extract_list_section(text, "efficiency_tips")
        success_factors = extract_list_section(text, "success_factors")
        
        return {
            "learning_patterns": learning_patterns,
            "improvement_areas": improvement_areas,
            "efficiency_tips": efficiency_tips,
            "success_factors": success_factors
        }
    except Exception as e:
        print(f"Error generating study insights: {e}")
        return {
            "learning_patterns": "Error analyzing learning patterns",
            "improvement_areas": ["Error occurred during AI processing"],
            "efficiency_tips": ["Unable to generate tips due to an error"],
            "success_factors": [f"Error: {str(e)}"]
        }

# Helper functions for parsing results
def extract_section(text, section_name):
    """Extract a section from semi-structured text"""
    if f'"{section_name}"' in text or f"'{section_name}'" in text:
        start_marker = f'"{section_name}":'
        if start_marker not in text:
            start_marker = f"'{section_name}':"
        
        start_idx = text.find(start_marker) + len(start_marker)
        
        # Find the end of this section (next comma not inside quotes, or closing brace)
        depth = 0
        in_quotes = False
        end_idx = start_idx
        
        for i in range(start_idx, len(text)):
            if text[i] == '"' and (i == 0 or text[i-1] != '\\'):
                in_quotes = not in_quotes
            elif not in_quotes:
                if text[i] == '{':
                    depth += 1
                elif text[i] == '}':
                    if depth == 0:
                        end_idx = i
                        break
                    depth -= 1
                elif text[i] == ',' and depth == 0:
                    end_idx = i
                    break
        
        if end_idx > start_idx:
            section = text[start_idx:end_idx].strip().strip('"\'[]{}').strip()
            return section
    
    # Default if extraction fails
    return f"Could not extract {section_name} section"

def extract_list_section(text, section_name):
    """Extract a list section from semi-structured text"""
    section = extract_section(text, section_name)
    
    # If it's already formatted like a list with brackets, parse it
    if section.startswith('[') and section.endswith(']'):
        items = section.strip('[]').split(',')
        return [item.strip().strip('"\'') for item in items if item.strip()]
    
    # Otherwise split by newlines and clean up
    items = section.split('\n')
    clean_items = []
    
    for item in items:
        # Remove list markers like "1.", "-", "*" etc.
        clean_item = item.strip()
        for marker in ['• ', '* ', '- ', '– ']:
            if clean_item.startswith(marker):
                clean_item = clean_item[len(marker):].strip()
        
        # Remove numbering like "1. ", "2. "
        if len(clean_item) > 2 and clean_item[0].isdigit() and clean_item[1:].startswith('. '):
            clean_item = clean_item[3:].strip()
            
        if clean_item:
            clean_items.append(clean_item)
    
    return clean_items if clean_items else ["No items found"] 