from flask_wtf import FlaskForm
from wtforms.fields.simple import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, Regexp, EqualTo, ValidationError

from models import User


# 用户注册表单
class RegistrationForm(FlaskForm):
    username = StringField('用户名',
                           validators=[
                               DataRequired(),
                               Length(min=2, max=20),
                               Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0, message='用户名必须仅有字母、数字、点或下划线')
                           ])
    password = PasswordField('密码',
                             validators=[
                                 DataRequired(),
                                 EqualTo('confirm_password', message='两次输入的密码需保持一致')
                             ])
    confirm_password = PasswordField('确认密码', validators=[DataRequired()])
    submit = SubmitField('注册')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('用户名已经被使用了！')
