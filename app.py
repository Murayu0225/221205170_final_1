from flask import Flask, jsonify, request
import sqlite3, hashlib, random, string, uuid


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


# ユーザ名重複確認
def check_user_func(username):
    conn = sqlite3.connect(dbname, isolation_level=None)
    cursor = conn.cursor()

    sql = """SELECT * FROM user WHERE name = ?"""
    data = (username,)
    cursor.execute(sql, data)
    res = cursor.fetchone()
    conn.commit()

    if res is None:
        return "OK"
    else:
        result = {"status": 409}
        return jsonify(result)


# 新規登録処理
def signup_func(username, nickname):
    conn = sqlite3.connect(dbname, isolation_level=None)
    cursor = conn.cursor()
    salt = str(randomname(10))
    sql = """INSERT INTO USER(id, name, user_nick_name, random_pass) VALUES(?, ?, ?, ?)"""
    data = (str(uuid.uuid4()), username, nickname, salt,)
    cursor.execute(sql, data)
    conn.commit()
    return jsonify({"status": 200, "salt": salt})


# 新規登録ハッシュ処理
def signup_auth_func(username, password):
    conn = sqlite3.connect(dbname, isolation_level=None)
    cursor = conn.cursor()
    sql = """update user set pass = ? where name = ? """
    data = (password, username,)
    cursor.execute(sql, data)
    res = cursor.fetchone()
    conn.commit()
    sql = """SELECT * FROM user WHERE name = ?"""
    data = (username,)
    cursor.execute(sql, data)
    res2 = cursor.fetchone()
    conn.commit()

    if res2 is not None:
        result = {"status": 200, "nickname": res2[3]}
        return jsonify(result)
    else:
        result = {"status": 401}
        return jsonify(result)


# ログイン処理
def signin_func(username):
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
        result = {"status": 200, "salt": res[4]}
        return jsonify(result)


# ログインハッシュ処理
def signin_auth_func(username, password):
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


@app.route('/signup', methods=['POST'])
def signup():
    try:
        username = request.json['u']
        user_conflict_check = check_user_func(username)
        if user_conflict_check == "OK":
            nickname = request.json['n']
            return signup_func(username, nickname)
        else:
            output = {"status": 409}
            return jsonify(output)
    except Exception as e:
        print(e)
        return jsonify({"status": 500, "error": str(e)})


@app.route('/signup/auth', methods=['POST'])
def signup_auth():
    try:
        username = request.json['u']
        password = request.json['p']
        output = signup_auth_func(username, password)
        return output
    except Exception as e:
        print(e)
        return jsonify({"status": 500, "error": str(e)})


@app.route('/signin', methods=['POST'])
def signin():
    try:
        username = request.json['u']
        output = signin_func(username)
        return output
    except Exception as e:
        print(e)
        return jsonify({"status": 500, "error": str(e)})


@app.route('/signin/auth', methods=['POST'])
def signin_auth():
    try:
        username = request.json['u']
        password = request.json['p']
        output = signin_auth_func(username, password)
        return output
    except Exception as e:
        print(e)
        return jsonify({"status": 500, "error": str(e)})


if __name__ == '__main__':
    app.run()
