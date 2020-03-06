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

key = []

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = "super secret key"

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/upload/img', methods=['POST'])
def upload_img():
    if request.method == 'POST':
        # img_base64 = request.form.get('imageData')       #原来的form方法
        # 获取传输的base64格式数据
        # 使用axios传送json数据，使用get_json方法
        data = request.get_json(silent=True)
        img_base64 = data['imageData']
        bookNo = data['bookNo']
        paperNo = data['paperNo']
        # img_base64 = request.form.get('imageData')
        # bookNo = request.form.get('bookNo')
        # paperNo = request.form.get('paperNo')
        img_base64 = img_base64.split(',')[1]
        img_jpg = base64.b64decode(img_base64)
        
        # 将图片以并保存
        filename = str(bookNo) + '_' + str(paperNo) + '.jpg'
        dir_name = os.path.join(app.config['UPLOAD_FOLDER'], str(bookNo))
        if not os.path.exists(dir_name):
            os.mkdir(dir_name)
        filename = os.path.join(dir_name, filename)
        
        file = open(filename, 'wb')
        file.write(img_jpg)
        file.close()
        
        # 若之前没有提交答案或数量不够40道，则返回错误信息
        # if len(key) != 40:
        #     return jsonify({'Status': 'BAD KEY NUM'})

        letters = model.getAns(filename, 0.5)
        dict = {}
        dict['letters'] = []
        for (index, item) in  enumerate(letters):
            letter = {
                'no': index + 1,
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

@app.route('/upload/result', methods=['GET', 'POST'])
def upload_result():
    if request.method == 'POST':
        # img_base64 = request.form.get('imageData')       #原来的form方法
        # 获取传输的base64格式数据
        # 使用axios传送json数据，使用get_json方法
        data = request.get_json(silent=True)
        bookNo = data['bookNo']
        paperNo = data['paperNo']
        writingAns = data['writingAns']

        # 将考生答案保存在csv文件中
        file = open(os.path.join(app.config['UPLOAD_FOLDER'], 'writingAns.csv'), 'a')
        s = str(bookNo) + ',' + str(paperNo)
        for t in writingAns:
            s = s + ',' + t
        s = s + '\n'
        file.write(s)
        file.close()
        return jsonify({'status': 'done'})

@app.route('/upload/key', methods = ['POST'])
def upload_answer():
    data = request.get_json()
    key_data = data['key']
    count = 1
    for x in key_data:
        if x['no'] == count:
            key.append({'option': x['option'], 'score': x['score']})
        count += 1

    print(key)
    if count != 40:
        print('!BAD KEY NUM!')
        return None
    else:
        return jsonify({'status': 'done'})
    # return jsonify({'key': key})

@app.route('/test', methods = ['GET'])
def test():
    return 'hello'

if __name__ == "__main__":
    app.run(host='0.0.0.0')