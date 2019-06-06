from flask import Flask
import json
import random

app = Flask(__name__)

USER_ID = '1'
promo_flag = True

meals = [{
    "title": "Chinken",
    "id": 1,
    "available": True,
    "picture": "",
    "price": 20.0,
    "category": 1
}, {
    "title": "Milk",
    "id": 2,
    "available": True,
    "picture": "",
    "price": 10.0,
    "category": 1
}]


def read_file(filename):
    opened_file = open(filename, 'r')
    data = json.loads(opened_file.read())
    opened_file.close()
    return data


def write_file(filename, data):
    opened_file = open(filename, 'w')
    opened_file.write(json.dumps(data))
    opened_file.close()


@app.route("/alive")
def alive():
    data = read_file('config.json')
    return json.dumps({"alive": data['alive']})


@app.route("/workhours")
def workhours():
    data = read_file('config.json')
    return json.dumps(data['workhours'])


@app.route("/promotion")
def promotion():
    promotion_number = random.randint(0, 2)
    promotions = read_file('promotions.json')
    return json.dumps(promotions[promotion_number])


@app.route("/promo/<code>")
def checkpromo(code):
    code = code.lower()
    promocodes = read_file('promo.json')
    for promocode in promocodes:
        if promocode["code"] == code:

            users_data = read_file('users.json')

            users_data[USER_ID]["promocode"] = code

            write_file('users.json', users_data)

            return json.dumps({"valid": True, "discount": promocode['discount']})
    return json.dumps({"valid": False})


@app.route("/meals")
def meals_route():
    global promo_flag
    users_data = read_file('users.json')

    promocode = users_data[USER_ID]['promocode']
    if (promocode is not None) and promo_flag:
        promocodes = read_file('promo.json')

        discount = 0

        for p in promocodes:
            if p['code'] == promocode:
                discount = p['discount']
        for m in meals:
            m['price'] = (1 - discount/100)*m['price']
        promo_flag = False
    return json.dumps(meals)


app.run("0.0.0.0", 8000)
