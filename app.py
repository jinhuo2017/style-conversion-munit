import os

from flask import Flask, request, jsonify
from server.predict import predict
from util import generate_image_id
from werkzeug.utils import secure_filename

app = Flask(__name__)

# 获取flask项目所在目录: ./style-conversion-munit
base_dir = os.path.abspath(os.path.dirname(__file__))
upload_relative_dir = 'results/uploads/'
processed_relative_dir = 'results/processed/'
# 允许的上传格式
IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'JPG', 'PNG', 'JPEG', 'gif', 'GIF'}


@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


# 检查文件名是否规范：判断文件名是否包含'.'并且后缀在白名单列表中
def allowed_file(filename):
    return ('.' in filename) and (filename.rsplit('.', 1)[1] in IMAGE_EXTENSIONS)


# 图片上传接口
@app.route('/upload', methods=['post'])
def upload():
    # 定义文件路径，如果不存在就创建
    username = request.form.get("username")
    print("base_dir", base_dir)
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
@app.route('/convert', methods=['GET', 'POST'])
# 传参：给定的图片路径、任务名称
def convert():
    if request.method == 'POST':
        # input: xxx.png eg: 0300.png
        input = request.form.get('input')
        # username: username eg: jinhuoyang
        username = request.form.get('username')
        task = request.form.get('task')
        processed = predict(input, task, username)

        print(f"{input}转换完成")
        return jsonify({'code': 1, 'msg': 'success', 'data': {'processed': processed}})
    return jsonify({'code': 0, 'msg': 'failed'})


if __name__ == '__main__':
    app.run()
