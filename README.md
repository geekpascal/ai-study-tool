# Study Tool - Time Management & Academic-Skill Balancing App

A Flask application designed to help students effectively manage their time by integrating academic studies with skill development.

## Features

- **Daily Schedule Automation**: Creates tailored daily plans with allocated times for studying and skill practice
- **Academic Material Integration**: Upload and track progress on course PDFs and study materials
- **Skill Development Tracking**: Manage skill practice and improvement over time
- **Exam Preparation Support**: Adjusts study plans based on upcoming deadlines
- **Personalized Recommendations**: Provides suggestions using Gemini AI API
- **User Profile Management**: Customize your profile settings and view personalized statistics
- **AI-Powered Learning Assistant**: 
  - Material analysis for targeted learning
  - Skill progress tracking and optimization
  - Personalized study insights
  - Web search for learning resources 
  - Dynamic schedule generation

## Tech Stack

- **Backend**: Python Flask
- **Database**: SQLAlchemy with SQLite
- **Frontend**: Tailwind CSS
- **Templates**: Jinja2
- **AI Integration**: Google Gemini 2.0 Flash
- **Web Search**: Tavily API

## Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd study-tool
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up environment variables (create a `.env` file):
   ```
   SECRET_KEY=your-secret-key
   DATABASE_URI=sqlite:///study_tool.db
   GEMINI_API_KEY=your-gemini-api-key  # Required for AI features
   TAVILY_API_KEY=your-tavily-api-key  # Required for web search features
   ```

5. Create the uploads directory:
   ```
   mkdir -p app/static/uploads
   ```

6. Run the application:
   ```
   python app.py
   ```

7. Visit `http://127.0.0.1:5000` in your web browser

## API Keys Setup

### Google Gemini API
1. Visit [Google AI Studio](https://makersuite.google.com/)
2. Sign in with your Google account
3. Get an API key for Gemini 2.0 Flash
4. Add it to your `.env` file as `GEMINI_API_KEY`

### Tavily API
1. Visit [Tavily API](https://tavily.com/)
2. Sign up for an account
3. Generate an API key
4. Add it to your `.env` file as `TAVILY_API_KEY`

## Usage

1. **Register/Login**: Create an account or sign in to access your dashboard
2. **Add Academic Materials**: Upload PDFs or enter study materials with deadlines
3. **Add Skills**: Enter skills you want to develop with details and resources
4. **Generate Daily Schedule**: The app creates a balanced daily plan
5. **Track Progress**: Update your progress on both academic materials and skills
6. **Get Recommendations**: Receive AI-powered suggestions for efficient learning
7. **Manage Your Profile**: Customize profile settings, view study statistics, and change your password
8. **Use AI Features**: Access AI-powered insights, recommendations, and web search for learning resources

## AI Features

- **Material Analysis**: Get AI insights about your study materials
- **Skill Progress Analysis**: Understand your skill development path
- **Schedule Optimization**: Get AI-generated optimized study schedules
- **Study Insights**: Analyze your learning patterns and get improvement tips
- **Personalized Recommendations**: Receive targeted advice for specific materials and skills
- **Web Search**: Find relevant learning resources and practice exercises

## Project Structure

- `/app`: Main application directory
  - `/controllers`: Route handlers
  - `/models`: Database models
  - `/services`: Business logic services including AI integrations
  - `/static`: Static files (CSS, JS, uploads)
  - `/templates`: Jinja2 templates

## User Profile Management

The application includes a comprehensive user profile management system:

- **View Profile**: See your account information and study activity summaries
- **Edit Profile**: Update your personal information, time zone, and study goals
- **Change Password**: Securely update your account password
- **Dashboard Statistics**: View detailed statistics about your study materials, skills, and schedules

## License

MIT License 