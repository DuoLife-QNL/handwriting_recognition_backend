import os, base64, time
from flask import Flask, flash, request, redirect, url_for, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
from net import Model

model = Model()

app = Flask(__name__)
CORS(app)

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
        data = request.get_json(silent=True)
        # img_base64 = request.form.get('imageData')
        img_base64 = data['imageData']
        img_base64 = img_base64.split(',')[1]
        img_jpg = base64.b64decode(img_base64)
        # 将图片以接收时间命名并保存
        now = time.strftime("%Y-%m-%d-%H_%M_%S",time.localtime(time.time())) 
        filename = now + '.jpg'
        filename = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file = open(filename, 'wb')
        file.write(img_jpg)
        file.close()

        letters = model.getAns(filename, 0.5)
        dict = {}
        dict['letters'] = []
        for item in letters:
            letter = {
                'class': item.classn,
                'box': item.boxesn,
                'score': item.scoren
            }
            dict['letters'].append(letter)
        if (len(letters) == 40):
            dict['valid'] = True
        else:
            dict['valid'] = False
        return jsonify(dict)
