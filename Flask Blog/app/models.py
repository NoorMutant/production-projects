from datetime import datetime, timezone, timedelta
from flask_login import UserMixin
import jwt
from app import db

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    posts = db.relationship('Post', backref='author', lazy=True)

    def get_reset_token(self, expires_sec=1800):
        token_data = {
            "user_id": self.id,
            "exp": datetime.now(timezone.utc) + timedelta(seconds=expires_sec)
        }
        return jwt.encode(token_data, db.app.config['SECRET_KEY'], algorithm="HS256")

    @staticmethod
    def verify_reset_token(token):
        try:
            data = jwt.decode(token, db.app.config['SECRET_KEY'], algorithms=["HS256"])
            return User.query.get(data['user_id'])
        except:
            return None

    def has_admin_privileges(self):
        return self.is_admin

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.now(timezone.utc))
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)