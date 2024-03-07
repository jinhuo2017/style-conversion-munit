from datetime import datetime

import pytz
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

db = SQLAlchemy()


# 定义Users类
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


# 定义History类
class ImageStatus(db.Model):
    __tablename__ = 'image_status'

    id = db.Column(db.Integer, primary_key=True)
    img_id = db.Column(db.String(20), unique=True, nullable=False)
    username = db.Column(db.String(20))
    date = db.Column(db.DateTime, nullable=False)
    img = db.Column(db.String(255), nullable=False)
    type = db.Column(db.Integer, nullable=False, default=0)  # 0: 图片在用户名下， 1: 图片在用户名-文件夹下
    folder = db.Column(db.String(255))
    status = db.Column(db.Integer, nullable=False, default=0)  # 0：未处理, 1：已处理

    # 构造方法
    def __init__(self, img_id, username, date, img, type, folder, status):
        self.img_id = img_id
        self.username = username
        self.date = date
        self.img = img
        self.type = type
        self.folder = folder
        self.status = status

    def __repr__(self):
        return f'<ImageStatus {self.img}>'
