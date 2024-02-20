import datetime
import random
import uuid


# 创建一个唯一的图片id
# 规则：年月日时分+4位随机数字
# eg: 2024010112349632 , 9542为随机数
def generate_image_id():
    # 基于时间的UUID
    unique_uuid = uuid.uuid1()
    # 当前时间的年月日时分部分
    current_time = datetime.datetime.now().strftime("%Y%m%d%H%M")
    # 4位随机数
    random_number = random.randint(1000, 9999)
    # 将当前时间、UUID的时间部分和随机数拼接成图片ID
    image_id = f"{current_time}{random_number}"
    return image_id


if __name__ == '__main__':
    curtime = generate_image_id()
    print(curtime)
