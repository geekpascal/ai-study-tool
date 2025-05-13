from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    email = db.Column(db.String(120), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Profile fields
    name = db.Column(db.String(100))
    time_zone = db.Column(db.String(50), default='UTC')
    study_goal = db.Column(db.String(200))
    bio = db.Column(db.String(500))
    last_login = db.Column(db.DateTime)
    
    # Relationships
    materials = db.relationship('Material', backref='owner', lazy='dynamic')
    skills = db.relationship('Skill', backref='owner', lazy='dynamic')
    schedules = db.relationship('Schedule', backref='owner', lazy='dynamic')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_study_stats(self):
        """Get summary of user's study statistics."""
        total_materials = self.materials.count()
        total_skills = self.skills.count()
        total_schedules = self.schedules.count()
        
        return {
            'total_materials': total_materials,
            'total_skills': total_skills,
            'total_schedules': total_schedules
        }
    
    def __repr__(self):
        return f'<User {self.username}>'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id)) 