from flask import Flask, render_template, request, jsonify, redirect, url_for
app = Flask(__name__)

import requests
from bs4 import BeautifulSoup

from pymongo import MongoClient
client = MongoClient('mongodb://test:sparta@ac-arc7jbv-shard-00-00.lfxuxob.mongodb.net:27017,ac-arc7jbv-shard-00-01.lfxuxob.mongodb.net:27017,ac-arc7jbv-shard-00-02.lfxuxob.mongodb.net:27017/Cluster0?ssl=true&replicaSet=atlas-3juyq2-shard-0&authSource=admin&retryWrites=true&w=majority')
db = client.dbsparta

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/membership')
def register():
    return render_template('register.html')

@app.route('/main')
def main():
    myname = 'C반3조'
    return render_template('main.html', name=myname)

@app.route('/recommend')
def recommend():
    return render_template('recommend.html')

@app.route("/recommend_get", methods=["GET"])
def recommend_get():
    users_list = list(db.users.find({}, {'_id': False}))
    return jsonify({'users': users_list})

@app.route('/subscribe')
def subscribe():
    return render_template('subscribe.html')

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