from flask import Flask, request, jsonify
from server.predict import predict

app = Flask(__name__)


@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


# 风格迁移接口
@app.route('/convert', methods=['GET', 'POST'])
# 传参：给定的图片路径、任务名称
def convert():
    if request.method == 'POST':
        # input: /xxx.png eg: /0300.png
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
