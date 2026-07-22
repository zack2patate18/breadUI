from flask import Flask, request, jsonify, render_template
import hashlib
import uuid
from app.classes.Server import Server

app = Flask(__name__, template_folder="../../templates",
            static_folder="../../static")

usernames: list[str] = []
passwords = []
tokens: dict[str, uuid.UUID] = {}
servers: Server = []

usernames.append('dev_test123')
devPass = hashlib.sha256()
devPass.update(b"devPass123")
devPass = devPass.hexdigest()

passwords.append(devPass)

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/dashboard')
def dashboard():
    print(tokens)
    token = request.args.get('token')
    username = request.args.get('username')

    if token is None or username is None:
        print("no token")
        return render_template('login.html')

    if tokens.get(username) != uuid.UUID(token):
        print("invalid token")
        return render_template('login.html')
    
    return render_template('dashboard.html')

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

@app.route('/api/signup', methods=['POST'])
def api_signup():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    passwordConfirmation = data.get('passwordConfirmation')

    if not username or not passwordConfirmation or not password:
        return jsonify({"message": "Username or password cannot be empty"}), 400

    if password != passwordConfirmation:
        return jsonify({"message": "The passwords needs to be the same"}), 400
    
    hashed_password = hashlib.sha256()
    hashed_password.update(password.encode())
    hashed_password = hashed_password.hexdigest()

    usernames.append(username)
    passwords.append(hashed_password)

    return jsonify({"message": "Account created"}), 200

app.run('0.0.0.0', 8080, True)