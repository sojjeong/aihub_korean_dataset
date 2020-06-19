# aihub_korean_dataset 

# Introduction
- Deep Learning Text Recognition 모델을 위한 한국어 글자체 이미지 데이터셋 재가공
- http://aihub.or.kr/aidata/133
- 데이터 및 json 레이블 파일은 위의 사이트에서 다운로드 받을 수 있습니다. (가입 필요할 수 있음)

# Updates
- 2020.06.17 repo 생성
- 2020.06.19 parser argument 추가

# Purpose 
- 이미지파일이 없는 경우 발생
- 레이블이 없는 경우 발생
- 잘못된 레이블 존재 `ex : '국ㅇㄴ'`
- 음수 값을 가진 좌표값 존재
- 이와 같은 문제점을 해결하기 위해 데이터 재가공 

# Environment
- `python 3.8`
- `pillow 7.0.0`
- `matplotlib 3.1.3`
- python 이 이미 깔려 있다면 `pip install -r requirements.txt`  

# Data
- input : 이미지, 레이블에 해당하는 json 파일
- output : 글자 단위의 이미지 파일 `ImageID_text.jpg`

# Usage
- `python json_crop.py --input_json_dir [json path] --input_img_dir [input image path] --output_dir [cropping image path]` 

# Future work
- --unit ['char or word'] 옵션 구현
- naming 변경
