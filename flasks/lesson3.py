from flask import Flask
import random
import json

app = Flask(__name__)

promotions = [
    "Скидка 15% по промокоду STEPIK",
    "Скидка 10% по промокоду DELIVERY",
    "Скидка 5% на все напитки"
]


@app.route("/promotion")
def promotion():
    promotion_number = random.randint(0, 2)
    return '{"promotion":' + promotions[promotion_number] + '}'


app.run("0.0.0.0", 8000)
