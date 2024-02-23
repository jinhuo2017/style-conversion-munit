import subprocess
import os

base_upload_address = '../../results/uploads/'
base_processed_address = '../../results/processed/'

config_dict = {
    'gta2city': os.path.join('./configs/gta2city.yaml'),
    'city2gta': os.path.join('./configs/gta2city.yaml'),
    'day2night': os.path.join('/configs/bdd_d2n.yaml'),
    'night2day': os.path.join('/configs/bdd_d2n.yaml'),
    'sunny2rainy': os.path.join('/configs/bdd_sunny2rainy.yaml'),
    'rainy2sunny': os.path.join('/configs/bdd_sunny2rainy.yaml'),
}

checkpoint_dict = {
    'gta2city': os.path.join('./outputs/gta2city/checkpoints/gen_00100000.pt'),
    'city2gta': os.path.join('./outputs/gta2city/checkpoints/gen_00100000.pt'),
}

direction_dict = {
    'gta2city': 1,
    'city2gta': 0
}


def predict(input, task, username):
    config = config_dict.get(task)
    input_folder = os.path.join(base_upload_address + username + '/')
    image_list = input
    output_folder = os.path.join(base_processed_address + username)
    checkpoint = checkpoint_dict.get(task)
    a2b = direction_dict.get(task)
    # 构建命令
    cmd = [
        'python', 'test_folder_predict.py',
        '--config', config,
        '--input_folder', input_folder,
        '--image_list', image_list,
        '--output_folder', output_folder,
        '--checkpoint', checkpoint,
        '--a2b', str(a2b)
    ]


    # 获取当前工作目录
    flask_dir = os.getcwd()
    model_dir = os.path.join(flask_dir, 'server/munit')

    # res_dir = input

    # 执行命令
    try:
        subprocess.run(cmd, check=True, cwd=model_dir)
        return input
    except subprocess.CalledProcessError as e:
        print(f"An predict error occurred: {e}")

