import os
from dotenv import load_dotenv
from app.services.gemini_service import get_gemini_recommendations

# Load environment variables
load_dotenv()

def test_gemini_api():
    """Test if the Gemini API is working properly"""
    
    print("Testing Gemini AI API integration...\n")
    
    # Check if API key is set
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("❌ GEMINI_API_KEY is not set in .env file")
        print("Please add your Gemini API key to your .env file:")
        print("GEMINI_API_KEY=your-api-key-here")
        return
    
    print("✅ GEMINI_API_KEY found in .env file")
    
    # Test the recommendation service
    print("\nFetching sample recommendations...")
    recommendations = get_gemini_recommendations(
        study_material="Python Programming",
        skill_name="Web Development",
        current_progress="50%"
    )
    
    # Check if recommendations were generated
    if not recommendations:
        print("❌ Failed to get recommendations")
        return
    
    # Display the recommendations
    print("\n✅ Successfully received recommendations from Gemini AI!")
    print("\n--- Academic Tips ---")
    for i, tip in enumerate(recommendations["academic_tips"], 1):
        print(f"{i}. {tip}")
    
    print("\n--- Skill Resources ---")
    for i, resource in enumerate(recommendations["skill_resources"], 1):
        print(f"{i}. {resource}")
    
    print("\n--- Study Plan Advice ---")
    print(recommendations["study_plan"])
    
    print("\nGemini AI integration is working correctly! 🎉")

if __name__ == "__main__":
    test_gemini_api() 