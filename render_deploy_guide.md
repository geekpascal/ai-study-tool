# Deploying UniqueSync to Render

This guide will help you deploy your UniqueSync application to Render.

## Prerequisites

1. A GitHub account with your code pushed to a repository
2. A Render account (sign up at https://render.com if you haven't already)
3. Your API keys for Gemini and Tavily (if using those services)

## Steps for Deployment

### 1. Prepare Your Repository

Make sure your repository has the following files:

- `requirements.txt` - Lists all Python dependencies
- `wsgi.py` - Entry point for the Gunicorn web server
- `Procfile` - Tells Render how to run your application
- `app.py` - Your Flask application

### 2. Set Up a New Web Service on Render

1. Log in to your Render dashboard
2. Click "New" and select "Web Service"
3. Connect your GitHub account and select your repository
4. Configure the service:
   - **Name**: Choose a name for your service (e.g., uniquesync)
   - **Environment**: Select "Python 3"
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn wsgi:app`
   - **Plan**: Select the free plan for testing or a paid plan for production

### 3. Configure Environment Variables

In the Render dashboard for your service, go to the "Environment" tab and add the following variables:

- `SECRET_KEY`: A secure random string for session encryption
- `DATABASE_URI`: Your database connection string (Render offers PostgreSQL)
- `GEMINI_API_KEY`: Your Google Gemini API key
- `TAVILY_API_KEY`: Your Tavily API key (if using)

### 4. Set Up a PostgreSQL Database

For a production deployment, you should use a PostgreSQL database instead of SQLite:

1. In your Render dashboard, click "New" and select "PostgreSQL"
2. Configure your database settings
3. Once created, copy the "External Database URL" from the Info tab
4. Add this URL as the `DATABASE_URI` environment variable for your web service

### 5. Deploy Your Application

1. After configuring everything, click "Create Web Service"
2. Render will build and deploy your application
3. Once deployment is complete, you can access your application via the provided URL

### 6. Troubleshooting

If you encounter issues with your deployment:

- Check the Render logs for error messages
- Verify that your environment variables are correctly set
- Ensure that your `wsgi.py` and `Procfile` are correctly configured
- Make sure your `requirements.txt` includes all necessary dependencies

### 7. Important Files

#### Procfile
```
web: gunicorn wsgi:app
```

#### wsgi.py
```python
from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run()
```

#### app.py
```python
from app import create_app

application = create_app()
app = application  # For compatibility with gunicorn

if __name__ == '__main__':
    app.run(debug=True)
```

## Next Steps

- Set up a custom domain name
- Configure SSL/TLS for secure connections
- Set up automatic database backups
- Configure scaling options for production use 