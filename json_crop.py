#-*- coding:utf-8 -*-

"""
1. json 파일 불러오기
2. 필요한 value 만 뽑아내기
    2-1. images의 id와 labels 의 image_id 매칭해야함.
3. 경로 찾아서 이미지 탐색
    3-1. 경로가 없으면 다음 iter 로 넘어가도록
4. 이미지에서 bbox 갯수만큼 for 문을 돌려 bbox crop
5. 저장시 잘라낸 단어의 이름으로 저장하도록.
    5-1. 글자 + 숫자 형태로 해서 중복된 파일명이 생기지 않도록 하자.

"""

import json
import numpy as np
import pathlib
import os
import matplotlib.pyplot as plt
import cv2

from PIL import Image
from pprint import pprint as pp


def json_open(path=None):
    with open(path, 'rt', encoding='UTF8') as f:
        data = json.load(f)
        images = data['images']
        labels = data['annotations']

    return images, labels


def images_open(images_dict):
    """
    json 에서 필요한 value만 뽑아낸 후 이미지 open을 위한 경로 작업
    :param images_dict: value dictionary
    :return: image path dictionary { 'image_id':image path }
    """
    top_path = "textinthewild"
    path_dict = {}

    for image_id, path_list in images_dict.items():
        image_type = path_list[0]
        file_name = path_list[1]

        file_path = os.path.join(top_path, image_type, file_name)
        is_path = os.path.exists(file_path)

        # input the image file path in dictionary
        # {'image_id':image path}
        if is_path:
            path_dict[image_id] = file_path
        else:
            continue

    # pp(path_dict)
    return path_dict


def images_crop(path_dict, labels_dict):
    """
    이미지 전체를 저장해서 리스트로 불러오는 짓은 좋은 방법이 아님
    그때,그때 경로를 읽어 open 한 후, crop 해 저장하는 방식으로 바꾸자.

    1. 같은 id를 가져온다.
    2. labels 에서 id 에 해당하는 딕셔너리를 가져온다.
    3. 각 텍스트별 바운딩 박스대로 crop
    4. crop 한 이미지는 id_text.jpg 로 저장한다.

    :param path_dict: image path dictionary {'image id':image path}
    :param labels_dict: label list {'image_id':{'text':bbox list}
    bbox = [left, top, w, h]
    :return:
    """

    for image_id, path in path_dict.items():
        is_file_exists = os.path.isfile(path)
        if is_file_exists is False:
            continue

        load_image = Image.open(path)
        bbox_dict = labels_dict.get(image_id)

        for bbox_text, bbox_coordinate in bbox_dict.items():
            text = bbox_text
            coordinate = []

            # 좌표 음수 에러 수정
            for i in bbox_coordinate:
                if i < 0:
                    i *= -1
                coordinate.append(i)

            left = coordinate[0]
            top = coordinate[1]
            w = coordinate[2]
            h = coordinate[3]
            right = left + w
            bottom = top + h

            crop_image = load_image.crop((left, top, right, bottom))

            print(image_id, text)
            write_path = "D:/textinthewild/{}_{}.jpg".format(image_id, text)

            crop_image.save(write_path)


def imshow(image):
    plt.imshow(image)
    plt.show()


def finding_image_value(images_list):
    """
    # 이미지 리스트 안의 딕셔너리에서 bbox list 뽑아내기
    # 이미지 리스트 안의 딕셔너리에서 file_name 뽑아내기

    :param images_list:
    :param labels_list:
    :return:
    """
    file_dict = {}

    for image_dict in images_list:
        image_id = image_dict['id']
        file_name = image_dict['file_name']
        image_type = image_dict['type']

        file_dict[image_id] = [image_type, file_name]

    # pp(file_dict)
    return file_dict


def finding_labels_value(labels_list):
    labels_dict = {}

    for label_dict in labels_list:
        image_id = label_dict['image_id']
        labels_dict[image_id] = {}

    for label_dict in labels_list:
        if label_dict['attributes']['class'] == 'character':
            image_id = label_dict['image_id']
            text = label_dict['text']

            is_not_ko = False

            # 두 글자로 잘못 되있는 레이블링 제외
            if len(text) > 1:
                continue
            # 한글 외 글자 제외
            for character in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890.,./\?<>~!@#$%^&*()_+-=;:` "''':
                if text == character:
                    is_not_ko = True

            if is_not_ko:
                continue

            bbox = label_dict['bbox']
            labels_dict[image_id][text] = bbox

    # == == == == == == == == == == == == == == == == == == == == == == ==
    # 공 value 제거
    key_list = []
    for key, value in labels_dict.items():
        if value == {}:
            key_list.append(key)

    for key in key_list:
        del labels_dict[key]
    # == == == == == == == == == == == == == == == == == == == == == == ==

    # pp(labels_dict)
    return labels_dict


def dict_compare(images_dict, labels_dict):
    # 없는 파일 label 제거
    remove_image_keylist = []
    remove_labels_keylist = []

    for key in labels_dict.keys():
        if not images_dict.get(key):
            remove_image_keylist.append(key)

    for key in images_dict.keys():
        if not labels_dict.get(key):
            remove_labels_keylist.append(key)

    # labels_key remove
    for key in remove_image_keylist:
        del labels_dict[key]

    # images_key remove
    for key in remove_labels_keylist:
        del images_dict[key]

    # print(len(images_dict), len(labels_dict))
    return images_dict, labels_dict


def main():
    images, labels = json_open(path='textinthewild_data_info.json')

    images_dict = finding_image_value(images)
    labels_dict = finding_labels_value(labels)

    images_dict, labels_dict = dict_compare(images_dict, labels_dict)
    image_path = images_open(images_dict)
    images_crop(image_path, labels_dict)


if __name__ == "__main__":
    main()