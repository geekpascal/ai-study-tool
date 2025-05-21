from app import create_app

application = create_app()
app = application  # For compatibility with gunicorn

if __name__ == '__main__':
    app.run(debug=True) 