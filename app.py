from flask import Flask, jsonify, request
import sqlite3
import hashlib


app = Flask(__name__)


def get_db_connection():
    import os
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(BASE_DIR, "products.db")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/init', methods = ["GET"])
def  init_db():
    conn = get_db_connection()
    conn.execute("""
                 CREATE TABLE IF NOT EXISTS products(
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 name TEXT NOT NULL,
                 price REAL NOT NULL
                 )
                 """)
    conn.execute("""
                 CREATE TABLE IF NOT EXISTS users(
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 username TEXT UNIQUE NOT NULL,
                 password TEXT NOT NULL
                 )
                 """)
    conn.commit()
    conn.close()
    return jsonify({"message": "Database init complete"})
    



@app.route('/')
def home():
    return jsonify({"message": "Hello from our first Flask server"})


@app.route('/register', methods = ["POST"])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get("password")

    if not username or not password:
        return jsonify({"message":"Missing Password or Username"}), 400
    
    hashed_password = hashlib.sha256(password.encode()).hexdigest()

    try:
        conn = get_db_connection()
        conn.execute('INSERT INTO users (username, password) VALUES (?,?)', (username, hashed_password))
        conn.commit()
        conn.close()
        return jsonify({'message': "User Registered"}), 201
    

    except sqlite3.IntegrityError:
        return jsonify({'message': 'Username already exists'}), 409
    

@app.route('/login', methods = ["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"message":"Missing Username or Password"})
    
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE  username = ? AND password = ?",(username, hashed_password)).fetchone()
    conn.close()

    if user: 
        return jsonify({"message":f"Welcome {username}!"})
    else:
        return jsonify({"message":"Invalid Credentials"}), 401
    





@app.route('/stuff', methods = ["GET"])
def getproducts():
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM products").fetchall()
    conn.close()
    return jsonify( [dict(row)for row in rows] )
    

@app.route("/stuff", methods= ["POST"])
def add_products():
    data = request.get_json() #recibo las respuestas del post
    name = data.get("name")
    price = data.get("price")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO products (name, price) VALUES (?,?)" , (name, price)) #lo pongo en la tabla
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    new_product= { #aca lo uso para mostrarlo
        "id": new_id,
        "name": name,
        "price": price
        
    }
    
    return jsonify({"message": "product added", "product": new_product}), 201

if __name__ == "__main__":
    with app.app_context():
        init_db()
    app.run(debug=True)