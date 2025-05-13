import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get Tavily API key from environment
TAVILY_API_KEY = os.getenv('TAVILY_API_KEY')

def check_api_key():
    """Check if Tavily API key is set"""
    return TAVILY_API_KEY is not None and TAVILY_API_KEY != ''

def search(query, search_depth="basic", max_results=5, include_domains=None, exclude_domains=None):
    """
    Search the web using Tavily API
    
    Parameters:
    - query: The search query string
    - search_depth: 'basic' or 'advanced'
    - max_results: Maximum number of results to return (1-10)
    - include_domains: List of domains to include in search results
    - exclude_domains: List of domains to exclude from search results
    
    Returns:
    - Dictionary with search results or error message
    """
    if not check_api_key():
        return {
            "success": False,
            "error": "Tavily API key not set",
            "results": []
        }
    
    # API endpoint
    url = "https://api.tavily.com/search"
    
    # Request payload
    payload = {
        "api_key": TAVILY_API_KEY,
        "query": query,
        "search_depth": search_depth,
        "max_results": max_results
    }
    
    # Add optional parameters if provided
    if include_domains:
        payload["include_domains"] = include_domains
    if exclude_domains:
        payload["exclude_domains"] = exclude_domains
    
    try:
        # Make the API call
        response = requests.post(url, json=payload)
        
        # Check if the request was successful
        if response.status_code == 200:
            results = response.json()
            return {
                "success": True,
                "results": results.get("results", []),
                "topic": results.get("topic", ""),
                "query": query
            }
        else:
            return {
                "success": False,
                "error": f"API request failed with status code {response.status_code}: {response.text}",
                "results": []
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"Error making API request: {str(e)}",
            "results": []
        }

def search_with_context(query, context, search_depth="basic", max_results=5):
    """
    Search the web with additional context using Tavily API
    
    Parameters:
    - query: The search query string
    - context: Additional context to guide the search
    - search_depth: 'basic' or 'advanced'
    - max_results: Maximum number of results to return (1-10)
    
    Returns:
    - Dictionary with search results or error message
    """
    # Combine query and context
    enhanced_query = f"{query} - Context: {context}"
    return search(enhanced_query, search_depth, max_results)

def search_learning_resources(topic, skill_level="intermediate", resource_type=None, max_results=5):
    """
    Search for learning resources on a specific topic
    
    Parameters:
    - topic: The topic to search for
    - skill_level: beginner, intermediate, advanced
    - resource_type: tutorial, course, documentation, etc.
    - max_results: Maximum number of results to return
    
    Returns:
    - Dictionary with search results or error message
    """
    # Create a specific query for learning resources
    query = f"best {resource_type + ' ' if resource_type else ''}{skill_level} learning resources for {topic}"
    
    # Include education and learning domains
    include_domains = [
        "coursera.org", "udemy.com", "edx.org", "khanacademy.org", 
        "freecodecamp.org", "w3schools.com", "udacity.com", "codecademy.com",
        "geeksforgeeks.org", "tutorialspoint.com", "stackoverflow.com", 
        "github.com", "medium.com", "dev.to", "docs.python.org"
    ]
    
    return search(query, "advanced", max_results, include_domains)

def enrich_material_with_web_data(material_title, material_description=None):
    """
    Enrich study material with additional web information
    
    Parameters:
    - material_title: The title of the study material
    - material_description: Optional description of the material
    
    Returns:
    - Dictionary with enriched information
    """
    if not check_api_key():
        return {
            "success": False,
            "error": "Tavily API key not set",
            "enriched_data": {}
        }
    
    query = material_title
    if material_description:
        query = f"{material_title} - {material_description}"
    
    # Search for the material
    search_results = search(query, "advanced", 3)
    
    if not search_results["success"]:
        return {
            "success": False,
            "error": search_results["error"],
            "enriched_data": {}
        }
    
    # Extract useful information from the search results
    enriched_data = {
        "additional_resources": [],
        "related_topics": [],
        "key_insights": []
    }
    
    # Process search results
    for result in search_results["results"]:
        # Add the result as a resource
        enriched_data["additional_resources"].append({
            "title": result.get("title", "Untitled Resource"),
            "url": result.get("url", ""),
            "content_snippet": result.get("content", "")[:200] + "..."
        })
        
    return {
        "success": True,
        "enriched_data": enriched_data,
        "query": query
    }

def search_practice_exercises(skill_name, skill_level="intermediate", max_results=3):
    """
    Search for practice exercises for a specific skill
    
    Parameters:
    - skill_name: The name of the skill
    - skill_level: beginner, intermediate, advanced
    - max_results: Maximum number of results to return
    
    Returns:
    - Dictionary with search results or error message
    """
    query = f"{skill_level} {skill_name} practice exercises projects challenges"
    
    return search(query, "advanced", max_results) 