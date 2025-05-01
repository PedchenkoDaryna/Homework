'''Скласти програму для роботи з базою даних, що містить інформацію
про постачальників товару. Для кожного постачальника вказано його назву та
контактні дані. У окремих таблицях БД зберігаються дані про товари а також
дані про постачальників товарів. Реалізувати функції додавання
постачальника, додавання товару, фіксації факту, що постачальник постачає
певний товар а також пошуку за назвою товару усіх постачальників, що
постачають товар та пошуку за назвою постачальника усіх товарів, що
постачає постачальник.'''
from flask import Flask, render_template, request
import sqlite3
app = Flask(__name__)
def get_db():
    conn = sqlite3.connect("suppliers.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as db:
        db.execute('''
        CREATE TABLE IF NOT EXISTS suppliers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            contact TEXT NOT NULL
        )''')
        db.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        )''')
        db.execute('''
        CREATE TABLE IF NOT EXISTS supplies (
            supplier_id INTEGER,
            product_id INTEGER,
            PRIMARY KEY (supplier_id, product_id),
            FOREIGN KEY (supplier_id) REFERENCES suppliers(id),
            FOREIGN KEY (product_id) REFERENCES products(id)
        )''')

init_db()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/add_supplier", methods=["POST"])
def add_supplier():
    name = request.form["name"]
    contact = request.form["contact"]
    with get_db() as db:
        db.execute("INSERT INTO suppliers (name, contact) VALUES (?, ?)", (name, contact))
    return "Постачальника додано!"

@app.route("/add_product", methods=["POST"])
def add_product():
    name = request.form["name"]
    with get_db() as db:
        db.execute("INSERT INTO products (name) VALUES (?)", (name,))
    return "Товар додано!"

@app.route("/add_supply", methods=["POST"])
def add_supply():
    supplier = request.form["supplier"]
    product = request.form["product"]
    with get_db() as db:
        s = db.execute("SELECT id FROM suppliers WHERE name=?", (supplier,)).fetchone()
        p = db.execute("SELECT id FROM products WHERE name=?", (product,)).fetchone()
        if s and p:
            db.execute("INSERT OR IGNORE INTO supplies (supplier_id, product_id) VALUES (?, ?)", (s["id"], p["id"]))
            return "Постачання зафіксовано!"
        return "Помилка: не знайдено постачальника або товару."

@app.route("/search_by_product", methods=["GET"])
def search_by_product():
    product = request.args.get("product")
    with get_db() as db:
        rows = db.execute('''
        SELECT suppliers.name, suppliers.contact FROM suppliers
        JOIN supplies ON suppliers.id = supplies.supplier_id
        JOIN products ON products.id = supplies.product_id
        WHERE products.name = ?
        ''', (product,)).fetchall()
    return render_template("results.html", rows=rows, label="Постачальники", query=product)

@app.route("/search_by_supplier", methods=["GET"])
def search_by_supplier():
    supplier = request.args.get("supplier")
    with get_db() as db:
        rows = db.execute('''
        SELECT products.name FROM products
        JOIN supplies ON products.id = supplies.product_id
        JOIN suppliers ON suppliers.id = supplies.supplier_id
        WHERE suppliers.name = ?
        ''', (supplier,)).fetchall()
    return render_template("results.html", rows=rows, label="Товари", query=supplier)

if __name__ == "__main__":
    app.run(debug=True)


