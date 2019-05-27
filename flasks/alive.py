from flask import Flask

app = Flask(__name__)

alive_state = False
workhours_open = "10:00"
workhours_closes = "22:00"
promotion_text = "Сегодня скидка 15% по промокоду stepik"


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
    if code == "stepik":
        return '{"valid":true,"discount":15}'
    elif code == "summer":
        return '{"valid":true,"discount":10}'
    elif code == "pleaseplease":
        return '{"valid:true,"discount":5}'
    else:
        return '{"valid":false}'


app.run("0.0.0.0", 8000)
