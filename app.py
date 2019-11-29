import os, base64, time
from flask import Flask, flash, request, redirect, url_for, jsonify
from werkzeug.utils import secure_filename
from net import Model

model = Model()

app = Flask(__name__)

UPLOAD_FOLDER = './storage'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = "super secret key"

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # 获取传输的base64格式数据
        img_base64 = request.form.get('imageData')
        # 将base64格式数据转换为jpg图片
        img_base64 = img_base64.split(b',')[1]
        img_jpg = base64.b64decode(img_base64)
        # 将图片以接收时间命名并保存
        now = time.strftime("%Y-%m-%d-%H_%M_%S",time.localtime(time.time())) 
        filename = now + '.jpg'
        filename = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file = open(filename, 'wb')
        file.write(img_jpg)
        file.close()

        # 返回json数据
        # pred_boxes, pred_class, pred_score = model.prediction(filename, 0.8)
        # dict = {}
        # dict['data'] = []
        # for i in range(len(pred_boxes)):
        #     item = {
        #         'class': pred_class[i],
        #         'box': pred_boxes[i],
        #         'score': pred_score[i]
        #     }

        letters = model.getAns(filename, 0.8)
        dict = {}
        if (len(letters) == 40):
            dict['valid'] = True
            dict['letters'] = []
            for item in letters:
                letter = {
                    'class': item.classn,
                    'box': item.boxesn,
                    'score': item.scoren
                }
                dict['letters'].append(letter)

        else:
            dict['valid'] = False
        return jsonify(dict)
