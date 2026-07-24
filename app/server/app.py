from flask import Flask, request, jsonify, render_template, redirect, session, url_for
from flask_socketio import SocketIO, emit, disconnect
import hashlib
from app.classes.Server import Server
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__, template_folder="../../templates",
            static_folder="../../static")

app.secret_key = os.environ["SECRET_KEY"]

socketio = SocketIO(app)

usernames: list[str] = []
passwords = []
servers: list[Server] = []

servers.append(Server("test", "test superflat world in creative", "1.20.1", "paper", 5, 0, server_list=servers))
servers[0].online = False

servers.append(Server("test", "test superflat world in creative", "1.20.1", "paper", 20, 2, server_list=servers))
servers[1].online = True

servers.append(Server("test", "test superflat world in creative", "1.20.1", "paper", 2, 1, server_list=servers))
servers[2].online = True

usernames.append('dev_test123')
devPass = hashlib.sha256()
devPass.update(b"devPass123")
devPass = devPass.hexdigest()

passwords.append(devPass)

@app.route('/')
def home():
    if "username" in session:
        return redirect(url_for('dashboard'))
    
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

@app.route('/server/<int:server_id>')
def server_route(server_id):
    if "username" not in session:
        return redirect('/')

    for server in servers:
        if server.server_id == server_id:
            return render_template('server.html', server_id=server_id)

    return render_template('404.html')

@app.errorhandler(404)
def not_found(e):
    return render_template('404.html')

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


@socketio.on("connect")
def on_connect():
    if "username" not in session:
        disconnect()

@socketio.on("getServersInfos")
def on_get_servers_infos():
    servers_infos: list[dict[str, int | str | bool]] = []

    for server in servers:
        current_server = {
            "name": server.name,
            "description": server.description,
            "online": server.online,
            "onlinePlayers": server.online_players,
            "maxPlayer": server.max_player,
            "version": server.version,
            "software": server.software,
            "id": server.server_id
        }

        servers_infos.append(current_server)

    emit("serversInfos", servers_infos)

# app.run('0.0.0.0', 8080, True)
socketio.run(app, "0.0.0.0", 8080, debug=True)