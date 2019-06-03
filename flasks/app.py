from flask import Flask
import json
import random

app = Flask(__name__)

alive_state = False
workhours_open = "10:00"
workhours_closes = "22:00"
promotion_text = "Сегодня скидка 15% по промокоду stepik"
promocodes = [
    {"code": "stepik", "discount": 15},
    {"code": "delivery", "discount": 10}
]

promotions = [
    "Скидка 15% по промокоду STEPIK",
    "Скидка 10% по промокоду DELIVERY",
    "Скидка 5% на все напитки"
]


@app.route("/alive")
def alive():
    return '{"alive":' + str(alive_state) + '}'


@app.route("/workhours")
def workhours():
    return '{"opens":"' + workhours_open + '","closes":' + workhours_closes + '}'


@app.route("/promotion")
def promotion():
    promotion_number = random.randint(0, 2)
    return '{"promotion":' + promotions[promotion_number] + '}'


@app.route("/promo/<code>")
def checkpromo(code):
    code = code.lower()
    for promocode in promocodes:
        if promocode["code"] == code:
            return json.dumps({"valid": True, "discount": promocode['discount']})
    return json.dumps({"valid": False})


app.run("0.0.0.0", 8000)
