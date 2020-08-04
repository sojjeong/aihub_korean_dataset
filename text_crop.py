#-*- coding:utf-8 -*-
import json
import os
import matplotlib.pyplot as plt
import argparse

from PIL import Image
# from pprint import pprint as pp

parser = argparse.ArgumentParser()
parser.add_argument('--input_json_dir', '-inJson', type=str, help='input json directory')
parser.add_argument('--input_img_dir', '-inImg', type=str, help='input image directory, before mode')
parser.add_argument('--output_dir', '-out', type=str, help='output image directory')
parser.add_argument('--unit', '-u', type=int, default=0, help='select text unit option[0:character,1:word,2:both text]')
parser.add_argument('--name', '-n', type=int, default=0, help='select naming option[0:id_gt, 1:gt_id]')

opt = parser.parse_args()


def json_open(json_dir, img_dir):
    """
    - json file open
    - image file name read
    :param path: input json dir, input image dir
    :return: image_data_list, label_data_list, image name list
    """
    with open(json_dir, 'rt', encoding='UTF8') as f:
        data = json.load(f)
        image_data_list = data['images']
        label_data_list = data['annotations']

    image_name_list = os.listdir(img_dir)

    return image_data_list, label_data_list, image_name_list


def finding_valid_image(image_data_list, image_name_list):
    """
    :param image_data_list: image data list
    :param image_name_list: image name list in input image dir
    :return: {'image_id': 'file_name'}
    """
    reverse_dict = {}
    image_dict = {}

    for i in range(len(image_data_list)):
        file_name = image_data_list[i]['file_name']
        image_id = image_data_list[i]['id']

        if image_data_list[i]['file_name'] in image_name_list:
            # 다른 아이디로 중복된 파일 이름이 존재함
            # 파일 이름을 key 로 사용해 중복 제거
            reverse_dict[file_name] = image_id

    # 관리를 위해 id : file_name 으로 변경
    for key, val in reverse_dict.items():
        image_dict[val] = key

    return image_dict


def finding_valid_label(label_data_list, image_dict):
    """
    finding label which has same image id in image_dict
    :param label_data_list:[{'id': , 'image_id': , 'attribues':{'class': character, word }, 'text': , 'bbox':[x,y coordinate]}]
    :param image_dict: {image_id:file_name}
    :return: labels_dict{'image id':[{id: , 'text':[bbox coordinate]}, {id: , 'text':[bbox coordinate]}....]}
    """
    valid_dict = {}

    # make blank list in the dictionary
    for key in image_dict:
        valid_dict[key] = []

    # search the same image_id
    for dict in label_data_list:
        image_id = dict['image_id']

        # default label text unit option
        unit_option = 0

        if dict['attributes']['class'] == 'character':
            unit_option = 0
        elif dict['attributes']['class'] == 'word':
            unit_option = 1

        if opt.unit == 2:
            unit_option = 2

        if opt.unit == unit_option:
            if image_id in image_dict:
                temp_dict = {}
                text = dict['text']

                # except for not characters
                is_not_ko = False
                for character in '.,./\?<>~!@#$%^&*()_+-=;:` "''':
                    if text == character:
                        is_not_ko = True

                # except for invalid length label and not character
                if is_not_ko or len(text) > 1:
                    continue

                temp_dict['id'] = dict['id']
                temp_dict[text] = dict['bbox']

                valid_dict[image_id].append(temp_dict)

    return valid_dict


def finding_path(image_dict, input_path):
    """
    modify the image dictionary for extracting value
    :param image_dict:
    :param input_path: input image path
    :return: image path dictionary {'image_id':image path}
    """
    path_dict = {}

    for image_id, path_list in image_dict.items():
        image_type = path_list[0]

        # match type name to input,output image folder name
        if image_type == 'product':
            image_type = 'Goods'
        elif image_type == 'sign':
            image_type = 'Signboard'
        elif image_type == 'traffic sign':
            image_type = 'Traffic_Sign'

        file_name = path_list[1]

        file_path = os.path.join(input_path, image_type, file_name)
        is_path = os.path.exists(file_path)

        # input the image file path in dictionary
        # {'image_id':image path}
        if is_path:
            path_dict[image_id] = file_path
        else:
            continue

    # pp(path_dict)
    return path_dict


def images_crop(path_dict, label_dict, output_path):
    """
    :param path_dict: image path dictionary {'image id':image path}
    :param label_dict: label list {'image_id':{'text':bbox list}
                            bbox = [left, top, w, h]
    :param output_path : output path for storing cropped image
    :return:
    """
    for image_id, path in path_dict.items():
        is_file_exists = os.path.isfile(path)
        if is_file_exists is False:
            continue

        load_image = Image.open(path)
        bbox_dict = label_dict.get(image_id)

        for bbox_text, bbox_coordinate in bbox_dict.items():
            text = bbox_text
            coordinate = []

            # modify negative coordinates
            for i in bbox_coordinate:
                if i < 0:
                    i *= -1
                elif i == 0:    # invalid h,w size changed to greater than 0
                    i = 1
                coordinate.append(i)

            left = coordinate[0]
            top = coordinate[1]
            w = coordinate[2]
            h = coordinate[3]
            right = left + w
            bottom = top + h

            crop_image = load_image.crop((left, top, right, bottom))

            # print(image_id, text)
            if opt.name == 0:
                write_path = "{}/{}_{}.jpg".format(output_path, image_id, text)
            elif opt.name == 1:
                write_path = "{}/{}_{}.jpg".format(output_path, text, image_id)

            crop_image.save(write_path)


def imshow(image):
    plt.imshow(image)
    plt.show()


def main(opt):
    image_data_list, label_data_list, image_name_list = json_open(json_dir=opt.input_json_dir, img_dir=opt.input_img_dir)

    valid_image_dict = finding_valid_image(image_data_list, image_name_list)
    valid_labels_dict = finding_valid_label(label_data_list, valid_image_dict)


if __name__ == "__main__":
    main(opt)
    # branch test