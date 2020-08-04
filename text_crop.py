#-*- coding:utf-8 -*-
import json
import os
import matplotlib.pyplot as plt
import argparse
from PIL import Image

parser = argparse.ArgumentParser()
parser.add_argument('--input_json_dir', '-inJson', type=str, default='data/textinthewild_data_info.json', help='input json directory')
parser.add_argument('--input_img_dir', '-inImg', type=str, default='data/book', help='input image directory, before mode')
parser.add_argument('--output_dir', '-out', type=str, default='data/crop_results', help='output image directory')
parser.add_argument('--unit', '-u', type=int, default=0, help='select text unit option[0:character,1:word,2:both text]')
parser.add_argument('--name', '-n', type=int, default=1, help='select naming option[0:id_textId_gt, 1:gt_id_textId]')

opt = parser.parse_args()

def json_open(json_dir, img_dir):
    """
    - json file open
    - image file name read
    :param: input json dir, input image dir
    :return: image_data_list, label_data_list, image name list
    """
    with open(json_dir, 'rt', encoding='UTF8') as f:
        data = json.load(f)
        image_data_list = data['images']
        label_data_list = data['annotations']

    image_name_list = os.listdir(img_dir)
    print("loading complete")
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

        if file_name in image_name_list:
            # exists duplicated file name haven another id
            # because dictionary does not allow duplicate keys,
            # so, use the file name as key
            reverse_dict[file_name] = image_id

    # reverse {file_name:id} -> {id : file_name}
    for key, val in reverse_dict.items():
        image_dict[val] = key

    print("finding valid image complete")
    return image_dict


def finding_valid_label(label_data_list, image_dict, input_unit_option):
    """
    finding label which has same image id in image_dict
    :param label_data_list:[{'id': , 'image_id': , 'attribues':{'class': character, word }, 'text': , 'bbox':[x,y coordinate]}]
    :param image_dict: {'image_id' : 'file_name'}
    :return: labels_dict{'image id':[{id:{'text':[bbox coordinate]}}, {id:{'text':[bbox coordinate]}}...]}
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

        if input_unit_option == 2:
            unit_option = 2

        if input_unit_option == unit_option:
            if image_id in image_dict:
                temp_dict = {}
                text = dict['text']

                # except for not characters
                if text is None:
                    continue

                # except for invalid length
                if unit_option == 0:
                    if len(text) > 1:
                        continue

                is_not_ch = False

                # check valid ascii value
                for ch in text:
                    ascii_ch = ord(ch)
                    if not((ascii_ch >= 44032 and ascii_ch <= 55203) or     # Korean
                           (ascii_ch >= 48 and ascii_ch <= 57) or           # Number
                            (ascii_ch >= 65 and ascii_ch <= 90) or          # English(capital)
                            (ascii_ch >= 97 and ascii_ch <= 122)):          # English(small)
                        is_not_ch = True

                if is_not_ch:
                    continue

                text_dict = {}
                text_dict[text] = dict['bbox']

                text_id = dict['id']
                temp_dict[text_id] = text_dict

                valid_dict[image_id].append(temp_dict)

    print("finding valid label complete")
    return valid_dict


def bbox_crop(valid_image_dict, valid_label_dict, intput_folder, output_folder):
    """
    valid text box crop in the valid image
    :param valid_image_dict:
    :param valid_label_dict:
    :return:
    """

    # make output folder
    if not os.path.exists(output_folder):
        os.mkdir(output_folder)

    for image_id, file_name in valid_image_dict.items():
        path = f'{intput_folder}/{file_name}'

        # check the dir
        is_file_exists = os.path.isfile(path)
        if not is_file_exists:
            continue

        load_image = Image.open(path)
        text_list = valid_label_dict.get(image_id)  # [{'00001' :  {'text':[bbox]}}, {'00001' :  {'text':[bbox]}}]

        for text_instance in text_list:
            print(text_instance)
            for id, box in text_instance.items():
                text_id = id
                text_bbox = box

            for text, bbox in text_bbox.items():
                # invalid h,w size changed to greater than 0
                coordinate = []

                for i in bbox:
                    if i < 0:
                        i *= -1
                    elif i == 0:
                        i = 1
                    coordinate.append(i)

                left = coordinate[0]
                top = coordinate[1]
                w = coordinate[2]
                h = coordinate[3]
                right = left + w
                bottom = top + h

                origin_x, origin_y = load_image.size

                # pass invalid w, h size
                if (w > origin_x or h > origin_y or
                    right > origin_x or bottom > origin_y):
                    continue

                crop_image = load_image.crop((left, top, right, bottom))

                # naming option
                if opt.name == 0:
                    write_path = "{}/{}_{}_{}.jpg".format(output_folder, image_id, text_id, text)
                elif opt.name == 1:
                    write_path = "{}/{}_{}_{}.jpg".format(output_folder, text, image_id, text_id)

                crop_image.save(write_path)
    print("cropping complete")


def imshow(image):
    plt.imshow(image)
    plt.show()


def main(opt):
    image_data_list, label_data_list, image_name_list = json_open(json_dir=opt.input_json_dir, img_dir=opt.input_img_dir)

    valid_image_dict = finding_valid_image(image_data_list, image_name_list)
    valid_labels_dict = finding_valid_label(label_data_list, valid_image_dict, opt.unit)

    bbox_crop(valid_image_dict, valid_labels_dict, opt.input_img_dir, opt.output_dir)


if __name__ == "__main__":
    main(opt)