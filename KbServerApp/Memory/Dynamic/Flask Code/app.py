from flask import Flask, jsonify, request
import sqlite3

app = Flask(__name__)

# Connect to the database
conn = sqlite3.connect('database.db')
c = conn.cursor()

# Routes
@app.route('/books', methods=['GET'])
def get_books():
    c.execute("SELECT * FROM Books")
    books = c.fetchall()
    return jsonify(books)

@app.route('/users', methods=['GET'])
def get_users():
    c.execute("SELECT * FROM Users")
    users = c.fetchall()
    return jsonify(users)

@app.route('/purchases', methods=['GET'])
def get_purchases():
    c.execute("SELECT * FROM Purchases")
    purchases = c.fetchall()
    return jsonify(purchases)

@app.route('/reviews', methods=['GET'])
def get_reviews():
    c.execute("SELECT * FROM Reviews")
    reviews = c.fetchall()
    return jsonify(reviews)



if __name__ == '__main__':
    app.run(debug=True)