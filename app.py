import hashlib
from datetime import timedelta

import jwt
import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template, request, jsonify, redirect, url_for

app = Flask(__name__)

import requests
from bs4 import BeautifulSoup

from pymongo import MongoClient

import certifi

client = MongoClient('mongodb://test:sparta@ac-arc7jbv-shard-00-00.lfxuxob.mongodb.net:27017,ac-arc7jbv-shard-00-01.lfxuxob.mongodb.net:27017,ac-arc7jbv-shard-00-02.lfxuxob.mongodb.net:27017/Cluster0?ssl=true&replicaSet=atlas-3juyq2-shard-0&authSource=admin&retryWrites=true&w=majority')
db = client.dbsparta

SECRET_KEY = 'SPARTA'

@app.route('/')
def home():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({'username': payload['id']})
        username = user_info['username']
        user_interest = user_info['category']
        return render_template('main.html', name=username, interest_list=user_interest)
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

# 회원가입 페이지로 연결
@app.route('/membership')
def register():
    return render_template('register.html')

# 회원가입 정보 DB로 POST
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

# DB에 중복되는 아이디가 있는지 확인
@app.route('/membership/check_dup', methods=['POST'])
def check_dup():
    username_receive = request.form['username_give']
    exists = bool(db.users.find_one({"username": username_receive}))
    return jsonify({'result': 'success', 'exists': exists})

# 각 게시판으로 연결
@app.route('/recommend')
def recommend():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({'username': payload['id']})
        username = user_info['username']
        user_interest = user_info['category']

        recommend_list = []
        for interest in user_info['category']:
            for recommend in db.favoritube.find({'cate': interest}, {'_id': False}):
                recommend_list.append(recommend)

        return render_template('recommend.html', name=username, recommend_list=recommend_list, interest_list=user_interest)
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))

@app.route('/mylist/<keyword>')
def mylist(keyword):
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({'username': payload['id']})
        username = user_info['username']
        user_interest = user_info['category']

        mylist = []
        for interest in user_info['category']:
            for my in db.mylist.find({'cate': interest}, {'_id': False}):
                mylist.append(my)

        return render_template('mylist.html', name=username, mylist=mylist,
                               interest_list=user_interest, word = keyword )
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


@app.route('/mylist_post' , methods=["POST"])
def mylist_post():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({'username': payload['id']})
        username = user_info['username']
        user_interest = user_info['category']

        url_receive = request.form['url_give']
        title_receive = request.form['title_give']
        comment_receive = request.form['comment_give']
        print(title_receive,comment_receive)
        db.mylist.update_one({'url': url_receive}, {'$set': {'title': title_receive}})
        db.mylist.update_one({'url': url_receive}, {'$set': {'comment': comment_receive}})


        return jsonify({'msg': '수정 완료!'})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))

@app.route('/subscribe')
def subscribe():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({'username': payload['id']})
        username = user_info['username']
        user_interest = user_info['category']
        return render_template('subscribe.html', name=username, interest_list=user_interest)
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


# 구독추가 정보를 DB로 POST
@app.route("/subscribe", methods=["POST"])
def subscribe_post():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({'username': payload['id']})
        username = user_info['username']
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
            'username' : username,
            'url': url_receive,
            'title': title_receive,
            'image': image,
            'cate': cate_receive,
            'comment': comment_receive
        }
        db.mylist.insert_one(doc)

        return jsonify({'msg': '추가 완료!'})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))

if __name__ == '__main__':
    app.jinja_env.add_extension('jinja2.ext.loopcontrols')
    app.run('0.0.0.0', port=5000, debug=True)
