#-*- coding:utf-8 -*-
import json
import os
import matplotlib.pyplot as plt
import argparse

from PIL import Image
from pprint import pprint as pp

parser = argparse.ArgumentParser()
parser.add_argument('--input_json_dir', '-inJson', type=str, help='input json directory')
parser.add_argument('--input_img_dir', '-inImg', type=str, help='input image directory, before mode')
parser.add_argument('--output_dir', '-out', type=str, help='output image directory')
parser.add_argument('--unit', '-u', type=str, default='char', help='select character or word for cropping')
parser.add_argument('--name', '-n', type=int, default=0, help='select naming option [0:id_gt, 1:gt_id]')

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


def finding_image_value(image_data_list, image_name_list):
    """
    :param images_list:
    :return: {'image_id':['type', file_name']}
    """

    """
    file_dict = {}

    for image_dict in image_data_list:
        image_id = image_dict['id']
        file_name = image_dict['file_name']
        image_type = image_dict['type']

        file_dict[image_id] = [image_type, file_name]

    # pp(file_dict)
    return file_dict
    """

    valid_image_list = []
    valid_image_id = []


def finding_labels_value(labels_list):
    """
    finding valid value in label dictionary
    :param labels_list: labels_list[{'image id': , 'attribues':{'class': character, word }, 'text': }]
    :returns: labels_dict{'image id':{'text' : [bbox coordinate]}}
    """
    labels_dict = {}

    for label_dict in labels_list:
        image_id = label_dict['image_id']
        labels_dict[image_id] = {}

    for label_dict in labels_list:
        image_id = label_dict['image_id']
        text = label_dict['text']

        if label_dict['attributes']['class'] == 'character':
            is_not_ko = False

            # except for not characters
            for character in '.,./\?<>~!@#$%^&*()_+-=;:` "''':
                if text == character:
                    is_not_ko = True

            # except for invalid length label and not character
            if is_not_ko or len(text) > 1:
                continue

        bbox = label_dict['bbox']
        labels_dict[image_id][text] = bbox

    # remove blank value
    key_list = []
    for key, value in labels_dict.items():
        if value == {}:
            key_list.append(key)

    for key in key_list:
        del labels_dict[key]

    # pp(labels_dict)
    return labels_dict


def dict_compare(image_dict, label_dict):
    """
    dictionary compare for removing invalid file
    :param image_dict:
    :param label_dict:
    :return: image_dict, label_dict
    """

    remove_image_keylist = []
    remove_labels_keylist = []

    for key in label_dict.keys():
        if not image_dict.get(key):
            remove_image_keylist.append(key)

    for key in image_dict.keys():
        if not label_dict.get(key):
            remove_labels_keylist.append(key)

    # labels_key delete
    for key in remove_image_keylist:
        del label_dict[key]

    # images_key delete
    for key in remove_labels_keylist:
        del image_dict[key]

    # print(len(images_dict), len(labels_dict))
    return image_dict, label_dict


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

    valid_images_dict = finding_image_value(image_data_list, image_name_list)
    valid_labels_dict = finding_labels_value(label_data_list)

    valid_images_dict, valid_labels_dict = dict_compare(valid_images_dict, valid_labels_dict)
    path_dict = finding_path(valid_images_dict, opt.input_img_dir)
    images_crop(path_dict, valid_labels_dict, opt.output_dir)


if __name__ == "__main__":1
    main(opt)