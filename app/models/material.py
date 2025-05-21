from app import db
from datetime import datetime

class Material(db.Model):
    __tablename__ = 'materials'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    file_path = db.Column(db.String(255))
    file_type = db.Column(db.String(50))
    total_pages = db.Column(db.Integer, default=0)
    current_page = db.Column(db.Integer, default=0)
    deadline = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    schedule_items = db.relationship('ScheduleItem', backref='material', lazy='dynamic')
    
    def progress_percentage(self):
        if self.total_pages == 0:
            return 0
        return int((self.current_page / self.total_pages) * 100)
    
    def remaining_days(self):
        if not self.deadline:
            return None
        delta = self.deadline - datetime.utcnow()
        return max(0, delta.days)
    
    def pages_per_day(self):
        if not self.deadline or self.total_pages == 0:
            return 0
        days_left = max(1, self.remaining_days())
        pages_left = max(0, self.total_pages - self.current_page)
        return round(pages_left / days_left)
    
    def __repr__(self):
        return f'<Material {self.title}>' 