import os
import urllib
import uuid

import requests
from flask import Flask, request
from flask_cors import CORS
import json
import random
import sqlite3

app = Flask(__name__)
CORS(app)

USER_ID = '1'


def get_cursor():
    connection = sqlite3.connect("database.db")
    c = connection.cursor()
    return c


def init_db():
    c = get_cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS meals(
        id integer PRIMARY KEY AUTOINCREMENT NOT NULL,
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
    CREATE TABLE IF NOT EXISTS promotions(
        id integer PRIMARY KEY,
        promotion text
    )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS orders(
            id text PRIMARY KEY,
            ordered text,
            meals text,
            summ real,
            status text,
            address text,
            user_id int           
        )
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

    c.execute("""
    INSERT INTO promotions VALUES (1, "Discount 15% with STEPIK promocode")
    """)

    c.execute("""
    INSERT INTO promotions VALUES (2, "Discount 10% with DELIVERY promocode")
    """)

    c.execute("""
    INSERT INTO promotions VALUES (3, "Discount 5% for all drinks")
    """)

    c.connection.commit()
    c.connection.close()


def fill_database():
    api_key = "7ee1cc6c2e4d5ecf10b9ab99b16c7e16"
    key_words = "cheese"
    page = 1
    params = {"key": api_key, "q": key_words, "page": page}
    url_string = "https://www.food2fork.com/api/search?" + urllib.parse.urlencode(params)
    r = requests.get(url_string)
    data = r.json()
    c = get_cursor()
    for page in range(1,5):
        for item in data['recipes']:
            c.execute("""
            INSERT INTO meals (title, available, picture, price, category) VALUES (?, ?, ?, ?, ?)
            """, [
                item['title'],
                1,
                item['image_url'],
                item['social_rank'] + random.randint(0, 100),
                1
            ])
            c.connection.commit()
    c.connection.close()


if not os.path.exists("database.db"):
    init_db()
    fill_database()


def read_file(filename):
    opened_file = open(filename, 'r')
    data = json.loads(opened_file.read())
    opened_file.close()
    return data


def write_file(filename, data):
    opened_file = open(filename, 'w')
    opened_file.write(json.dumps(data))
    opened_file.close()


def fire_discount(price, discount):
    return price * (1.0 - discount / 100)


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
    promotion_number = random.randint(1, 3)

    c = get_cursor()
    c.execute("""
    SELECT promotion FROM promotions WHERE id = ?
    """, (promotion_number,))
    result = c.fetchone()
    return json.dumps({"promotion": result[0]})


@app.route("/promocode/<code>")
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
    result = c.fetchone()

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
            'price': fire_discount(discount, price),
            'category': category
        })

    return json.dumps(meals)


@app.route("/orders", methods=["GET", "POST"])
def orders():
    c = get_cursor()

    if request.method == "GET":
        user_orders = []
        for order in c.execute("""SELECT id, ordered, meals, summ, status, address FROM orders WHERE user_id = ?""",
                               (int(USER_ID),)):
            order_id, ordered, order_meals, summ, status, address = order
            user_orders.append({
                'id': order_id,
                'ordered': ordered,
                'meals': order_meals,
                'summ': summ,
                'status': status,
                'address': address
            })
        return json.dumps(user_orders)
    elif request.method == "POST":
        raw_data = request.data.decode("utf-8")
        data = json.loads(raw_data)

        user_promocode = data['promocode']

        c.execute("""
        SELECT discount FROM promocodes
        WHERE code = ?
        """, (user_promocode,))
        result = c.fetchone()

        discount = 0
        if result is not None:
            discount = result[0]

        summ = 0.0
        for user_meal_id in data['meals']:
            c.execute("""SELECT price FROM meals WHERE id == ?""", (user_meal_id,))
            price = c.fetchone()[0]
            summ += fire_discount(price, discount)

        new_order_id = str(uuid.uuid4())
        new_order = [new_order_id, "", str(data['meals']), summ, "accepted", "", int(USER_ID)]

        c.execute("""INSERT INTO orders VALUES (?, ?, ?, ?, ?, ?, ?)""", new_order)

        c.connection.commit()
        c.connection.close()

        return json.dumps({'order_id': new_order_id})


@app.route("/order/<order_id>", methods=["DELETE"])
def one_order(order_id):
    c = get_cursor()
    if c.execute("""SELECT * FROM orders WHERE status == "accepted" AND id == ?""", (order_id,)).rowcount > 0:
        c.execute("""
        UPDATE orders
        SET status = "cancelled"
        WHERE id = ?
        """, (order_id,))
        c.connection.commit()
        c.connection.close()
        return "True"
    return "False", 404


@app.route("/activeorder", methods=["GET", "DELETE"])
def activeorder():
    c = get_cursor()

    if request.method == "GET":
        return find_active_order(c)
    elif request.method == "DELETE":
        if find_active_order(c)[0] is not "":
            c.execute("""
            UPDATE orders
            SET status = "cancelled"
            WHERE status == "accepted" AND user_id == ?
            """, (int(USER_ID),))
            c.connection.commit()
            c.connection.close()
            return "True"
        return "False", 404


def find_active_order(c):
    c.execute("""
        SELECT id, ordered, meals, summ, status, address FROM orders
        WHERE status == "accepted" AND user_id == ?
        """, (int(USER_ID),))
    result = c.fetchone()
    if result is not None:
        order_id, ordered, meals, summ, status, address = result
        return json.dumps({
            'id': order_id,
            'ordered': ordered,
            'meals': meals,
            'summ': summ,
            'status': status,
            'address': address
        })
    return "", 404


app.run("0.0.0.0", 8090)
