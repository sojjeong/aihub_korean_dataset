# aihub_korean_dataset 

# Introduction
- Deep Learning Text Recognition 모델을 위한 한국어 글자체 이미지 데이터셋 재가공
- http://aihub.or.kr/aidata/133
- 데이터 및 json 레이블 파일은 위의 사이트에서 다운로드 받을 수 있습니다. (가입 필요할 수 있음)

# Updates
- 2020.06.17 repo 생성
- 2020.06.19 parser argument 추가
- 2020.06.29 잘못된 레이블에 대한 예외 처리 추가, json 파일 내 type을 input, output 폴더명과 같도록 매칭
- 2020.08.04 유효 레이블 재구성하는 딕셔너리 형태 변경, 한글,영어,숫자 가능, 기호나 한글 모음 자음으로 분리된 잘못된 레이블 예외처리 추가, crop 시 생기는 사이즈 에러 예외처리 추가

# Purpose 
- 이미지파일이 없는 경우 발생
- 레이블이 없는 경우 발생
- 오타가 있는 레이블 존재 `ex : '국ㅇㄴ'`
- 음수 값을 가진 좌표값 존재
- 잘못된 높이, 너비 값 존재
- 이와 같은 문제점을 해결하기 위해 데이터 재가공 

# Environment
- `python 3.8`
- `pillow >= 7.0.0`
- `matplotlib >= 3.1.3`
- python 이 이미 깔려 있다면 `pip install -r requirements.txt`  

# Data
- input : 이미지, 레이블에 해당하는 json 파일
- output : 텍스트 이미지 파일 `ImageID_text_ID_text.jpg or text_ImageID_textID.jpg`
- json 파일 내 정답이 아예 잘못된 경우에 대해서는 예외처리하지 못했기 때문에 (ex:'젊'이란 글자에 '젋'이라고 레이블링이 되어 있는 경우) 직접 검수하셔야 합니다.

# Usage
<pre><code>
python json_crop.py --input_json_dir=[json path] \
                    --input_img_dir=[input image path] \
                    --output_dir=[cropping image path] \
                    --unit=[unit option 0:character, 1:word, 2:both] \ 
                    --name=[naimng option 0:ImageID_text_ID_text, 1:text_ImageID_textID]
</code></pre>
