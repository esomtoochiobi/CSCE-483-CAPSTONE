from flask import Flask

app = Flask(__name__)

@app.route('/')
def howdy_world():
    return '<h1>Howdy, world!</h1>'

