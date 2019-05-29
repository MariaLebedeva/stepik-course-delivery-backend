from flask import Flask
import json

app = Flask(__name__)

alive_state = False
workhours_open = "10:00"
workhours_closes = "22:00"
promotion_text = "Сегодня скидка 15% по промокоду stepik"
promocodes =[{"code":"STEPIK","discount":15},{"code":"DELIVERY","discount":10}]


@app.route("/alive")
def alive():
    return '{"alive":' + str(alive_state) + '}'


@app.route("/workhours")
def workhours():
    return '{"opens":"' + workhours_open + '","closes":' + workhours_closes + '}'


@app.route("/promotion")
def promotion():
    return '{"promotion":' + promotion_text + '}'


@app.route("/promo/<code>")
def checkpromo(code):
    for promocode in promocodes:
        if promocode["code"] == code:
            return json.dumps()
    return json.dumps()


app.run("0.0.0.0", 8000)
