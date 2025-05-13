from app import db
from datetime import datetime

class Skill(db.Model):
    __tablename__ = 'skills'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50))
    proficiency_level = db.Column(db.Integer, default=1)  # 1-10 scale
    target_level = db.Column(db.Integer, default=10)
    resources = db.Column(db.Text)  # JSON string of resources
    last_practiced = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    schedule_items = db.relationship('ScheduleItem', backref='skill', lazy='dynamic')
    
    def progress_percentage(self):
        if self.target_level == 0:
            return 0
        return int((self.proficiency_level / self.target_level) * 100)
    
    def days_since_last_practice(self):
        if not self.last_practiced:
            return None
        return (datetime.utcnow() - self.last_practiced).days
    
    def __repr__(self):
        return f'<Skill {self.name}>' 