#############################################
# <date> : 2020.11.05
# <description>
# crop 한 문자 이미지의 가로, 세로 비율로 
# horizontal, vertical 분류해 따로 저장
#############################################

import os
import argparse
import matplotlib.pyplot as plt
from PIL import Image

parser = argparse.ArgumentParser()
parser.add_argument('--input_img_dir', '-inImg', type=str, default='images/', help='input image directory, before mode')
parser.add_argument('--output_dir', '-out', type=str, default='output/', help='output image directory')

opt = parser.parse_args()

def ratio_classification(file_list):
    # 이미지 가로 
    # 세로 비율에 따라 분류
        
    horizontal_path = f'{opt.output_dir}/horizontal'
    vertical_path = f'{opt.output_dir}/vertical'
    temp_path = f'{opt.output_dir}/temp'

    if not os.path.exists(horizontal_path):
        os.mkdir(horizontal_path)

    if not os.path.exists(vertical_path):
        os.mkdir(vertical_path)

    if not os.path.exists(temp_path):
        os.mkdir(temp_path)

    for file_name in file_list:
        file_path = f'{opt.input_img_dir}/{file_name}'
        image = Image.open(file_path)
        size = image.size   # (width, height) tuple

        if size[0] > size[1]:
            image.save(f'{horizontal_path}/{file_name}')
        elif size[0] < size[1]:
            image.save(f'{vertical_path}/{file_name}')
        else:
            image.save(f'{temp_path}/{file_name}')


if __name__ == "__main__":
    file_list = os.listdir(opt.input_img_dir)
    ratio_classification(file_list)