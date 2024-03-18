import os

from flask import Flask, request, jsonify, send_from_directory, flash, session
from flask_wtf.csrf import generate_csrf
from werkzeug.exceptions import NotFound
from werkzeug.security import generate_password_hash

from forms import RegistrationForm
from models import User, db
from server.predict import predict
from util import generate_image_id, allowed_file
from werkzeug.utils import secure_filename
from flask_login import LoginManager, login_user, current_user, login_required, logout_user

app = Flask(__name__)
# 数据库相关配置
HOSTNAME = "127.0.0.1"
PORT = 3306
USERNAME = "root"
PASSWORD = "root"
DATABASE = "style_conversion"
app.config[
    'SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{USERNAME}:{PASSWORD}@{HOSTNAME}:{PORT}/{DATABASE}?charset=utf8mb4'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'TfPcOu5'  # 用于保护表单
app.config['WTF_CSRF_ENABLED'] = False
db.init_app(app)

with app.app_context():
    db.create_all()

# 获取flask项目所在目录: ./style-conversion-munit
base_dir = os.path.abspath(os.path.dirname(__file__))
upload_relative_dir = 'results/uploads/'
processed_relative_dir = 'results/processed/'

# 实例化扩展类
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = '没有登录'


@login_manager.unauthorized_handler
def unauthorized():
    # 返回自定义的 JSON 响应
    return jsonify({'code': 401, 'error': '请先登录'}), 401


# 创建用户加载回调函数，接受用户 ID 作为参数
@login_manager.user_loader
def load_user(user_id):
    user = User.query.get(int(user_id))  # 用 ID 作为 User 模型的主键查询对应的用户
    return user  # 返回用户对象


@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


# 生成csrf令牌
@app.route('/csrf-token', methods=['GET'])
def get_csrf_token():
    # 生成 CSRF 令牌
    token = generate_csrf()
    print(token)
    # 将 CSRF 令牌存储在 session 中
    session['csrf_token'] = token
    # 返回 CSRF 令牌
    return jsonify({'csrf_token': token})


#  用户注册
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()

    if form.validate_on_submit():

        password = form.password.data
        password_hash = generate_password_hash(password)
        user = User(username=form.username.data, password_hash=password_hash)

        db.session.add(user)
        db.session.commit()

        flash('你的账号已经成功注册，现在可以登录了！', 'success')
        return jsonify({'code': 0, 'msg': '注册成功'})
    else:
        print(form.errors)  # 打印出验证失败的错误信息
    return jsonify({'code': 1005, 'msg': '返回注册页面'})


# 用户登录
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return jsonify({'code': 1001, 'msg': '用户已登录'})
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not username or not password:
            flash('Invalid input.')
            return jsonify({'code': 1002, 'msg': 'username或password为空'})

        user = User.query.filter_by(username=username).first()
        # 验证用户名和密码是否一致
        if username == user.username and user.validate_password(password):
            # 登入用户
            login_user(user)
            flash('Login success.')
            session['username'] = current_user.username
            return jsonify({'code': 0, 'msg': '登录成功'})

        flash('Invalid username or password.')  # 如果验证失败，显示错误消息
        return jsonify({'code': 1003, 'msg': '无效的用户名或密码'})
    return jsonify({'code': 1004, 'msg': '返回登录页面'})


# 用户登出
@app.route('/logout')
@login_required  # 用于视图保护
def logout():
    logout_user()  # 登出用户
    flash('Goodbye.')
    session.pop('username', None)
    return jsonify({'code': 1004, 'msg': '返回登录页面'})


# 图片上传接口
@app.route('/upload', methods=['post'])
@login_required  # 登录保护
def upload():
    # 定义文件路径，如果不存在就创建
    # username = request.form.get("username")
    # 直接从session中获取username
    username = session.get('username')

    upload_dir = os.path.join(base_dir, upload_relative_dir + username + "/")
    processed_dir = os.path.join(base_dir, processed_relative_dir + username + "/")
    if not os.path.exists(upload_dir):
        print("creating upload_dir: ", upload_dir)
        os.makedirs(upload_dir)
    if not os.path.exists(processed_dir):
        print("creating processed_dir: ", processed_dir)
        os.makedirs(processed_dir)

    img = request.files.get('img_name')
    if img and allowed_file(img.filename):
        # 确保文件名安全
        cur_img_name = secure_filename(img.filename)

        # 获取文件后缀
        _, ext = os.path.splitext(cur_img_name)
        # 移除点号
        ext = ext[1:]

        img_name = generate_image_id() + '.' + ext
        img.save(os.path.join(upload_dir, img_name))
        return jsonify({'code': 1, 'msg': 'success', 'data': {'img_name': img_name}})
    else:
        return jsonify({'code': 0, 'msg': '文件上传失败'})


# 风格迁移接口
@login_required  # 登录保护
@app.route('/convert', methods=['GET', 'POST'])
# 传参：给定的图片路径、任务名称
def convert():
    if request.method == 'POST':
        # input: xxx.png eg: 0300.png
        input = request.form.get('input')
        # username: username eg: tom
        # username = request.form.get('username')
        # 直接从session中获取username
        username = session.get('username')

        task = request.form.get('task')
        processed = predict(input, task, username)

        print(f"{input}转换完成")
        return jsonify({'code': 1, 'msg': 'success', 'data': {'processed': processed}})
    return jsonify({'code': 0, 'msg': 'failed'})


# 图片展示
@login_required  # 登录保护
@app.route('/show', methods=['GET'])
def show_image():
    # username = request.args.get('username')
    # 直接从session中获取username
    username = session.get('username')

    # img_type 0: 原始图 1: 处理后的图像
    img_type = request.args.get('type')
    filename = request.args.get('filename')
    try:
        # 安全检查：确保没有使用 '..' 来访问文件夹路径之外的文件
        if '..' in filename or filename.startswith('/') or '../' in username or username.startswith('/'):
            raise ValueError("无效的username或filename")

        if img_type == '0':
            relative_dir = upload_relative_dir
        elif img_type == '1':
            relative_dir = processed_relative_dir
        else:
            raise ValueError('type类型为空')

        file_dir = os.path.join(base_dir, relative_dir, username)

        if not os.path.isdir(file_dir):
            raise NotFound(f"Image directory {file_dir} not found")

        # send_from_directory 安全发送位于指定文件夹中的文件
        return send_from_directory(file_dir, filename)
    except Exception as e:
        # 捕捉到任何发送过程中的异常，返回500内部服务器错误
        app.logger.error(f"Error while sending file {filename}: {str(e)}")
        return "An error occurred while trying to send the file.", 500


##############################################################################winggggggggggggggg
from PIL import Image
import io
import base64


# 图片批量上传接口
@login_required  # 登录保护
@app.route('/multi-upload', methods=['POST'])
def multi_upload():
    # 获取用户名
        # 直接从session中获取username
    username = session.get('username')
    print("base_dir", base_dir)
    upload_dir = os.path.join(base_dir, upload_relative_dir + username + "/")
    processed_dir = os.path.join(base_dir, processed_relative_dir + username + "/")
    if not os.path.exists(upload_dir):
        print("creating upload_dir: ", upload_dir)
        os.makedirs(upload_dir)
    if not os.path.exists(processed_dir):
        print("creating processed_dir: ", processed_dir)
        os.makedirs(processed_dir)
    filename_list = []  # 用于存储所有更名后的文件名
    for file in request.files.getlist('img_name'):
        if file and allowed_file(file.filename):
            cur_filename = secure_filename(file.filename)
            # 获取文件后缀
            _, ext = os.path.splitext(cur_filename)
            # 移除点号
            ext = ext[1:]

            file_name = generate_image_id() + '.' + ext
            file.save(os.path.join(upload_dir, file_name))
            filename_list.append(file_name)
        #     return jsonify({'code': 1, 'msg': 'success', 'data': {'img_name': file_name}})
        # else:
        #     return jsonify({'code': 0, 'msg': '文件上传失败'})
    return jsonify({'code': 1, 'msg': 'success', 'data': {'img_name': filename_list}})


# 批量风格迁移接口
@login_required  # 登录保护
@app.route('/multi-convert', methods=['GET', 'POST'])
# 传参：给定的图片路径、任务名称
def multi_convert():
    if request.method == 'POST':
        # input: xxx.png eg: 0300.png
        input_list = request.form.getlist('input')
        # username: username eg: jinhuoyang
            # 直接从session中获取username
        username = session.get('username')
        task = request.form.get('task')

        input_str = ''
        for img_name in input_list:
            input_str += (img_name + ',')
        input_str = input_str[:-1]
        processed = predict(input_str, task, username)

        print(f"{input}转换完成")
        return jsonify({'code': 1, 'msg': 'success', 'data': {'processed': input_list}})
    return jsonify({'code': 0, 'msg': 'failed'})


# 批量展示接口
@login_required  # 登录保护
@app.route('/multi-show', methods=['GET'])
def multi_show_image():
        # 直接从session中获取username
    username = session.get('username')
    # img_type 0: 原始图 1: 处理后的图像
    img_type = request.args.get('type')
    filename_list = request.args.getlist('filename')  # 将存储所有要展示的图片的名字，使用列表进行存储
    try:
        # 安全检查：确保没有使用 '..' 来访问文件夹路径之外的文件
        if '../' in username or username.startswith('/'):
            return jsonify({'code': 0, 'msg': '无效的username'})
        for filename in filename_list:
            if filename.startswith('/') or '..' in filename:
                return jsonify({'code': 0, 'msg': '无效的filename'})

        if img_type == '0':
            relative_dir = upload_relative_dir
        elif img_type == '1':
            relative_dir = processed_relative_dir
        else:
            return jsonify({'code': 0, 'msg': '无效的type'})

        file_dir = os.path.join(base_dir, relative_dir, username)

        if not os.path.isdir(file_dir):
            return jsonify({'code': 0, 'msg': f"Image directory {file_dir} not found"})

        image_data = []
        for filename in filename_list:
            filepath = os.path.join(file_dir, filename)

            if os.path.isfile(filepath):
                with Image.open(filepath) as img:
                    byte_arr = io.BytesIO()
                    img.save(byte_arr, format='PNG')  ########！！！！！！！！！此处仅支持png格式的图片，在编解码时均认为图片格式为png！！！！！！！！！！！
                    encoded_image = base64.encodebytes(byte_arr.getvalue()).decode('ascii')
                    image_data.append(encoded_image)
        return jsonify({'code': 1, 'msg': 'success', 'data': {'images': image_data}})
    except Exception as e:
        # 捕捉到任何发送过程中的异常，返回500内部服务器错误
        app.logger.error(f"Error while sending file {filename_list}: {str(e)}")
        return "An error occurred while trying to send the file.", 500


###################################################################winggggggggggggggg


if __name__ == '__main__':
    app.run()
