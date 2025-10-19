from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import enum

class UserRole(enum.Enum):
    ADMIN = 'admin'
    STAFF = 'staff'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128))
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    role = db.Column(db.Enum(UserRole), nullable=False, default=UserRole.STAFF)
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    stock_ins = db.relationship('StockIn', backref='user', lazy=True)
    stock_outs = db.relationship('StockOut', backref='user', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        return self.role == UserRole.ADMIN
    
    def is_staff(self):
        return self.role == UserRole.STAFF
    
    def get_role_name(self):
        return self.role.value
    
    @staticmethod
    def get_role_choices():
        return [(role.value, role.value.capitalize()) for role in UserRole]
    
    def __repr__(self):
        return f'<User {self.username} ({self.role.value})>'

# THIS is what makes current_user work:
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))