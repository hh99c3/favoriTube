from flask import Flask, render_template, request, jsonify
app = Flask(__name__)

from pymongo import MongoClient
client = MongoClient('mongodb+srv://test:sparta@cluster0.ydgg3.mongodb.net/Cluster0?retryWrites=true&w=majority')
db = client.dbsparta


@app.route('/')
def login():
    return render_template('login.html')

@app.route('/membership')
def register():
    return render_template('register.html')


@app.route('/main')
def main():
    myname = 'kelly'
    return render_template('recommend.html', name=myname)

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)