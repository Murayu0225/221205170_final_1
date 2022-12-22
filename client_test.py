import requests
import hashlib
import json

userid = "pict_test"
password = "pict_test_pass"

response = requests.get('http://127.0.0.1:5000/login?u={}'.format(userid))

res_json = json.loads(response.text)

if response.status_code == 200:
    if res_json['status'] == 200:
        salt = str(res_json['salt'])
        hash_pass = hashlib.sha256((password + salt).encode('utf-8')).hexdigest()
    elif res_json['status'] == 404:
        print("User not found")
        exit()
else:
    print("Network error.")
    exit()

response = requests.get('http://127.0.0.1:5000/auth?u={}&p={}'.format(userid, hash_pass))

res_json = json.loads(response.text)

if response.status_code == 200:
    if res_json['status'] == 200:
        print("Hello, world!")
        print(str(res_json['nickname']))
    elif res_json['status'] == 401:
        print("Authentication failed.")
        exit()
else:
    print("Network error.")
    exit()
