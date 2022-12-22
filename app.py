from flask import Flask, jsonify, request
import sqlite3
import hashlib
import random
import string


dbname = './db/user.db'


# ソルトする文字列生成
def randomname(n):
    randlst = [random.choice(string.ascii_letters + string.digits) for i in range(n)]
    return ''.join(randlst)


# パスワードハッシュ処理（ハッシュ、ソルト）
def calculate_hash(password):
    salt = randomname(10)
    hash_pass = hashlib.sha256((password + salt).encode('utf-8')).hexdigest()
    return hash_pass, salt

# データ追加用
# import uuid
# name = "pict_test"
# password = "pict_test_pass"
# nickname = "[test user]pict"
#
# hash_pass, salt = calculate_hash(password)
#
# dbname = './db/user.db'
# conn = sqlite3.connect(dbname, isolation_level=None)
# cursor = conn.cursor()
# sql = """INSERT INTO user VALUES(?, ?, ?, ?, ?)"""
#
# data = (str(uuid.uuid4()), str(name), str(hash_pass), str(nickname), str(salt))
# cursor.execute(sql, data)
# conn.commit()
# ここまで


# ログイン処理
def login_func(username):
    conn = sqlite3.connect(dbname, isolation_level=None)
    cursor = conn.cursor()

    sql = """SELECT * FROM user WHERE name = ?"""
    data = (username,)
    cursor.execute(sql, data)
    res = cursor.fetchone()
    conn.commit()

    if res is None:
        result = {"status": 404}
        return jsonify(result)
    else:
        result = {"status": 200, "salt": res[4], "token": "none"}
        return jsonify(result)


# ハッシュ処理
def auth_func(username, password):
    conn = sqlite3.connect(dbname, isolation_level=None)
    cursor = conn.cursor()

    sql = """SELECT * FROM user WHERE name = ?"""
    data = (username,)
    cursor.execute(sql, data)
    res = cursor.fetchone()
    conn.commit()

    if res[2] == password:
        result = {"status": 200, "nickname": res[3]}
        return jsonify(result)
    else:
        result = {"status": 401}
        return jsonify(result)


app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Auth System'


@app.route('/login', methods=['GET'])
def login():
    username = request.args.get('u')
    output = login_func(username)
    return output


@app.route('/auth', methods=['GET'])
def auth():
    username = request.args.get('u')
    password = request.args.get('p')
    output = auth_func(username, password)
    return output

if __name__ == '__main__':
    app.run()
