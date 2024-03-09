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


# 定义ImageStatus类
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

    def history_to_dict(self):
        return {
            "date": self.date.strftime("%Y-%m-%d"),
            "img": self.img,
            "folder": self.folder if self.folder else ""
        }


def save_image_status(img_id, img_name, username, type_, status, folder):
    # 查询数据库中是否有该img_id的数据
    record = ImageStatus.query.filter_by(img_id=img_id).first()
    if record:
        # 如果存在，检查status是否一致，不一致则更新
        if record.status != status:
            record.status = status
            db.session.commit()
    else:
        # 先对各个数据进行处理
        img_time_str = img_id[:12]
        img_datetime = datetime.strptime(img_time_str, '%Y%m%d%H%M')  # 转换为datetime对象

        # 如果不存在，添加新记录到数据库
        new_record = ImageStatus(
            img_id=img_id,
            username=username,
            date=img_datetime,
            img=img_name,
            type=type_,
            folder=folder,
            status=status
        )
        db.session.add(new_record)
        db.session.commit()


# 根据文件名、用户名、转换状态更新image_status
def update_image_status_by_img_and_status(input, status):
    img_id = input[:16]
    # 查询数据库中是否有该img_id的数据
    record = ImageStatus.query.filter_by(img_id=img_id).first()
    if record:
        if record.status != status:
            record.status = status
            db.session.commit()

