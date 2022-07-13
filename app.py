import hashlib
from datetime import timedelta

import jwt
import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template, request, jsonify, redirect, url_for
app = Flask(__name__)

from pymongo import MongoClient
client = MongoClient('mongodb://test:sparta@ac-arc7jbv-shard-00-00.lfxuxob.mongodb.net:27017,ac-arc7jbv-shard-00-01.lfxuxob.mongodb.net:27017,ac-arc7jbv-shard-00-02.lfxuxob.mongodb.net:27017/Cluster0?ssl=true&replicaSet=atlas-3juyq2-shard-0&authSource=admin&retryWrites=true&w=majority')
db = client.dbsparta

SECRET_KEY = 'SPARTA'

@app.route('/')
def home():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])

        return render_template('main.html')
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))

@app.route('/login')
def login():
    msg = request.args.get("msg")
    return render_template('login.html', msg=msg)

@app.route('/sign_in', methods=['POST'])
def sign_in():
    # 로그인
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']

    pw_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    result = db.users.find_one({'username': username_receive, 'password': pw_hash})

    if result is not None:
        from datetime import datetime
        payload = {
         'id': username_receive,
         'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 24)  # 로그인 24시간 유지
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

        return jsonify({'result': 'success', 'token': token})
    # 찾지 못하면
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})

@app.route('/membership')
def register():
    return render_template('register.html')

@app.route('/membership/save', methods=['POST'])
def sign_up():
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']
    category_receive = request.form.getlist('category_give')

    password_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    doc = {
        "username": username_receive,
        "password": password_hash,
        "category": category_receive
     }
    db.users.insert_one(doc)
    return jsonify({'result': 'success'})

@app.route('/membership/check_dup', methods=['POST'])
def check_dup():
    username_receive = request.form['username_give']
    exists = bool(db.users.find_one({"username": username_receive}))
    return jsonify({'result': 'success', 'exists': exists})

@app.route('/main')
def main():
    myname = 'C반3조'
    return render_template('main.html', name=myname)

@app.route('/recommend/<keyword>')
def recommend(keyword):
    myname = 'C반3조'
    users = list(db.users.find({}, {'_id': False}))
    return render_template('recommend.html', users= users , name = myname , word = keyword)

@app.route('/subscribe')
def subscribe():
    myname = 'C반3조'
    return render_template('subscribe.html', name = myname)

@app.route("/subscribe", methods=["POST"])
def subscribe_post():
    title_receive = request.form['title_give']
    url_receive = request.form['url_give']
    cate_receive = request.form['cate_give']
    comment_receive = request.form['comment_give']

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
    data = requests.get(url_receive, headers=headers)

    soup = BeautifulSoup(data.text, 'html.parser')

    image = soup.select_one('meta[property="og:image"]')['content']


    doc = {
        'url': url_receive,
        'title': title_receive,
        'image': image,
        'cate': cate_receive,
        'comment': comment_receive
    }
    db.users.insert_one(doc)

    return jsonify({'msg': '추가 완료!'})

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
