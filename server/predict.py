import subprocess
import os

base_upload_address = '../../results/uploads/'
base_processed_address = '../../results/processed/'

config_dict = {
    'gta2city': './configs/gta2city.yaml',
    'city2gta': './configs/gta2city.yaml',
    'day2night': '/configs/bdd_d2n.yaml',
    'night2day': '/configs/bdd_d2n.yaml',
    'sunny2rainy': '/configs/bdd_sunny2rainy.yaml',
    'rainy2sunny': '/configs/bdd_sunny2rainy.yaml',
}

checkpoint_dict = {
    'gta2city': './outputs/gta2city/checkpoints/gen_00100000.pt',
    'city2gta': './outputs/gta2city/checkpoints/gen_00100000.pt',
}

direction_dict = {
    'gta2city': 1,
    'city2gta': 0
}


def predict(input, task, username):
    config = config_dict.get(task)
    input_folder = base_upload_address + username + input
    output_folder = base_processed_address + username
    checkpoint = checkpoint_dict.get(task)
    a2b = direction_dict.get(task)
    # 构建命令
    cmd = [
        'python', 'test_folder_predict.py',
        '--config', config,
        '--input_folder', input_folder,
        '--output_folder', output_folder,
        '--checkpoint', checkpoint,
        '--a2b', str(a2b)
    ]

    # 获取当前工作目录
    flask_dir = os.getcwd()
    print("cur_dir: ", flask_dir)

    # 设置正确的工作目录
    model_dir = flask_dir + '/server/munit'  # munit的目录路径
    os.chdir(model_dir)

    res_dir = output_folder + input

    # 执行命令
    try:
        subprocess.run(cmd, check=True)
        os.chdir(flask_dir)
        return res_dir
    except subprocess.CalledProcessError as e:
        os.chdir(flask_dir)
        print(f"An predict error occurred: {e}")
