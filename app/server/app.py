import shutil

from flask import Flask, request, jsonify, render_template, redirect, session, url_for
from flask_socketio import SocketIO, emit, disconnect
import hashlib
from app.classes.Server import Server
from dotenv import load_dotenv
import os
import json

load_dotenv()

app = Flask(__name__, template_folder="../../templates",
            static_folder="../../static")

app.secret_key = os.environ["SECRET_KEY"]

socketio = SocketIO(app)

usernames: list[str] = []
passwords = []
servers: list[Server] = []

softwares: list[str] = ["vanilla"]
versions: list[str] = ["26.2"]

servers_dir: str = "servers"

usernames.append('dev_test123')
devPass = hashlib.sha256()
devPass.update(b"devPass123")
devPass = devPass.hexdigest()

passwords.append(devPass)

def list_servers():
    global servers
    folders: list[str] = [
        f for f in os.listdir(servers_dir)
        if os.path.isdir(os.path.join(servers_dir, f))
    ]

    servers = []

    for fo in folders:
        for file_name in os.listdir(os.path.join(servers_dir, fo)):
            if file_name == "breadUI_metadata.json":
                with open(os.path.join(servers_dir, fo, file_name), 'r') as f:
                    data: dict = json.load(f)
                    new_server: Server = Server.from_dict(data)
                    servers.append(new_server)

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

@app.route('/server/add')
def add_server():
    if "username" not in session:
        return redirect('/')

    return render_template('add-server.html')

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

@app.route('/api/get-softwares', methods=['GET'])
def api_get_software():
    if "username" not in session:
        return jsonify({}), 401

    return jsonify({"softwares": softwares}), 200

@app.route('/api/get-versions', methods=['GET'])
def api_get_versions():
    if "username" not in session:
        return jsonify({}), 401

    return jsonify({"versions": versions})

@app.route('/api/server/create', methods=['POST'])
def create_server():
    data = request.get_json()

    name = data["name"]
    description = data["description"]
    version = data["version"]
    software = data["software"]
    max_players = data["max_players"]
    port = data["port"]

    newServer: Server = Server(name, description, version, software, max_players, port, server_list=servers)
    servers.append(newServer)

    return jsonify({
        "message": "Server created successfully!"
    }), 201

@app.route('/api/server/list', methods=['GET'])
def api_server_list():
    if "username" not in session:
        return jsonify({"message": "unauthorized"}), 401

    return jsonify({"servers": [s.to_dict() for s in servers]})

@app.route('/api/server/delete', methods=['POST'])
def api_server_delete():
    if "username" not in session:
        return jsonify({"message": "unauthorized"}), 401

    data = request.get_json()

    server_id = int(data["server_id"])

    if not server_id:
        return jsonify({"message": "invalid request"}), 400

    for server in servers:
        if server.server_id == server_id:
            shutil.rmtree(os.path.join(server.root_dir, servers_dir, server.server_root_dir))
            servers.remove(server)
            break

    else:
        return jsonify({"message": "invalid request"}), 400

    return jsonify({"message": "server deleted successfully"}), 200

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

list_servers()

# app.run('0.0.0.0', 8080, True)
socketio.run(app, "0.0.0.0", 8080, debug=True)