from flask import Flask, request, jsonify, render_template
import hashlib
import uuid

app = Flask(__name__, template_folder="../../templates",
            static_folder="../../static")

usernames: list[str] = []
passwords = []
tokens: dict[str, uuid.UUID] = {}

usernames.append('dev_test123')
devPass = hashlib.sha256()
devPass.update(b"devPass123")
devPass = devPass.hexdigest()

passwords.append(devPass)

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"message": "invalid request"}), 400
    
    hashed_password = hashlib.sha256()
    hashed_password.update(password.encode())
    hashed_password = hashed_password.hexdigest()

    if username not in usernames or hashed_password not in passwords:
        return jsonify({"message": "invalid username or password"}), 401
    
    temp_token: uuid.UUID = uuid.uuid4()
    tokens[username] = temp_token

    return jsonify({"temp_token": temp_token, "message": "logged in"}), 200

app.run('0.0.0.0', 8080, True)