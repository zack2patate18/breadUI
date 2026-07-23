from flask import Flask, request, jsonify, render_template, redirect, session
import hashlib
from app.classes.Server import Server
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__, template_folder="../../templates",
            static_folder="../../static")

app.secret_key = os.environ["SECRET_KEY"]

usernames: list[str] = []
passwords = []
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
    if "username" not in session:
        return redirect('/')
    
    return render_template('dashboard.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

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
    
    session["username"] = username

    return jsonify({"message": "logged in"}), 200

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