from flask import Flask
app = Flask(__name__)


@app.route("/")
def hello():
    return "Hello"

@app.route("/alive")
def alive():
    return '{"alive": true}'

app.run("0.0.0.0", 8000)