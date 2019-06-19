import os

from flask import Flask
import json
import random
import sqlite3

app = Flask(__name__)

USER_ID = '1'

meals = [{
    "title": "Chicken",
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


def get_cursor():
    connection = sqlite3.connect("database.db")
    c = connection.cursor()
    return c


def init_db():
    c = get_cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS meals(
        id integer PRIMARY KEY,
        title text,
        available int,
        picture text,
        price real,
        category integer
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS promocodes(
        id integer PRIMARY KEY,
        code text,
        discount real
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id integer PRIMARY KEY,
        promocode text
    )
    """)

    c.execute("""
    INSERT INTO meals VALUES (1, "Chicken", 1, "", 20.0, 1)
    """)

    c.execute("""
    INSERT INTO meals VALUES (2, "Milk", 1, "", 10.0, 1)
    """)

    c.execute("""
    INSERT INTO promocodes VALUES (1, "stepik", 15.0)
    """)

    c.execute("""
    INSERT INTO promocodes VALUES (2, "delivery", 10.0)
    """)

    c.execute("""
    INSERT INTO users VALUES (1, null)
    """)

    c.connection.commit()
    c.connection.close()


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
def promo(code):
    c = get_cursor()
    c.execute("""
     SELECT * FROM promocodes WHERE code = ?
     """, (code,))

    result = c.fetchone()
    if result is None:
        return json.dumps({"valid": False})

    promo_id, promo_code, promo_discount = result
    c.execute("""
    UPDATE users
    SET promocode = ?
    WHERE id = ?
    """, (promo_code, int(USER_ID)))
    c.connection.commit()
    c.connection.close()
    return json.dumps({"valid": True, "discount": promo_discount})


@app.route("/meals")
def meals_route():
    c = get_cursor()
    c.execute("""
    SELECT discount FROM promocodes
    WHERE code = (
        SELECT promocode FROM users
        WHERE id = ?
    )
    """, (int(USER_ID),))
    result = c .fetchone()

    discount = 0
    if result is not None:
        discount = result[0]

    meals = []

    for meals_info in c.execute("SELECT * FROM meals"):
        meals_id, title, available, picture, price, category = meals_info
        meals.append({
            'id': meals_id,
            'title': title,
            'available': bool(available),
            'picture': picture,
            'price': price * (1.0 - discount / 100),
            'category': category
        })

    return json.dumps(meals)

if not os.path.exists("database.db"):
    init_db()

app.run("0.0.0.0", 8000)
