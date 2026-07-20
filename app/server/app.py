from flask import Flask, request, jsonify, render_template

app = Flask(__name__, template_folder="../../templates",
            static_folder="../../static")

@app.route('/')
def home():
    return render_template('login.html')

app.run('0.0.0.0', 8080, True)