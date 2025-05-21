from app import db
from datetime import datetime

class Schedule(db.Model):
    __tablename__ = 'schedules'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    description = db.Column(db.Text)
    date = db.Column(db.Date, default=datetime.utcnow().date)
    start_date = db.Column(db.Date, default=datetime.utcnow().date)
    end_date = db.Column(db.Date, default=datetime.utcnow().date)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    items = db.relationship('ScheduleItem', backref='schedule', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Schedule {self.title}>'
    
    # Helper method to get date for templates that might expect it
    def get_display_date(self):
        return self.date if self.date else self.start_date

class ScheduleItem(db.Model):
    __tablename__ = 'schedule_items'
    
    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    item_type = db.Column(db.String(20))  # 'academic' or 'skill'
    title = db.Column(db.String(100))
    description = db.Column(db.Text)
    completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign keys
    schedule_id = db.Column(db.Integer, db.ForeignKey('schedules.id'))
    material_id = db.Column(db.Integer, db.ForeignKey('materials.id'), nullable=True)
    skill_id = db.Column(db.Integer, db.ForeignKey('skills.id'), nullable=True)
    
    def duration_minutes(self):
        start_dt = datetime.combine(datetime.today(), self.start_time)
        end_dt = datetime.combine(datetime.today(), self.end_time)
        return (end_dt - start_dt).seconds // 60
    
    def __repr__(self):
        return f'<ScheduleItem {self.title} ({self.start_time}-{self.end_time})>' 