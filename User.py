from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    # 用户名
    username = db.Column(db.String(20))
    # 用户密码哈希值
    password_hash = db.Column(db.String(128))

    # 设置密码，生成密码哈希值
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    # 校验密码
    def validate_password(self, password) -> bool:
        return check_password_hash(self.password_hash, password)
