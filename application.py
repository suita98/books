import os

import requests
import json

from flask import Flask, session, render_template, request, redirect, url_for
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Establish connection with database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

@app.route("/", methods=['GET', 'POST'])
def index():
    if not is_logged_in():
        return redirect(url_for('login'))
    else:
        user = db.execute('SELECT * FROM users WHERE id = :id;', {'id': session['id']}).fetchone()
    if request.method == 'GET':
        return render_template("index.html", user=user)
    if request.method == 'POST':
        search_string = request.form['search_string']
        books = db.execute('''
            SELECT * FROM books WHERE LOWER(isbn) LIKE :search_string OR
            LOWER(title) LIKE :search_string OR
            LOWER(author) LIKE :search_string;
            ''', {'search_string': f'%{search_string}%'}).fetchall()
        if not books:
            return render_template("index.html", message="No books were found", user=user)
        return render_template("search_results.html", books=books, user=user)


@app.route("/register", methods=['GET', 'POST'])
def register():
    '''Implementation of registration page'''
    if is_logged_in():
        # If user is already logged in we add to the list of messages a relevant message
        try:
            messages.append("You are already registered")
        except NameError:
        # If list of messages doesn't exist - we create it
            messages = ["You are already registered"]
        user = db.execute('SELECT * FROM users WHERE id = :id;', {'id': session['id']}).fetchone()
        return render_template('index.html', messages=messages, user=user)
    if request.method == 'GET':
        return render_template('register.html')
    if request.method == 'POST':
        name = request.form['name']
        login = request.form['login']
        email = request.form['email']
        password = request.form['password']
        # TODO: keep hashed password instead of plain text
        # TODO: user is unique
        try:
            db.execute('INSERT INTO users (name, login, email, password) VALUES (:name, :login, :email, :password)', 
                {'name': name, 'login': login, 'email': email, 'password': password})
            db.commit()
            return "user saved"
        except Exception as e:
            return "user not saved\n" + str(e)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if is_logged_in():
        try:
            messages.append("You are already logged in")
        except NameError:
            messages = ["You are already logged in"]
        user = db.execute('SELECT * FROM users WHERE id = :id;', {'id': session['id']}).fetchone()
        return render_template('index.html', messages=messages, user=user)
    
    if request.method == 'GET':
        return render_template('login.html')
    
    if request.method == 'POST':
        login = request.form['login']
        password = request.form['password']
        user = db.execute('SELECT * FROM users WHERE login = :login;', {'login': login}).fetchone()
        
        if user is None:
            return "User not found"
        
        if user.password != password:
            return 'Password doesnt match'
        
        session['id'] = user.id
        return redirect(url_for('index'))            
            

@app.route("/logout", methods=['GET'])
def logout():
    session.pop('id', None)
    return redirect(url_for('index'))

    
@app.route("/book/<id>", methods=['GET', 'POST'])
def book(id):
    if not is_logged_in():
        return redirect(url_for('login'))
    else:
        user = db.execute('SELECT * FROM users WHERE id = :id;', {'id': session['id']}).fetchone()

    errors = []
    book = db.execute('SELECT * FROM books WHERE id = :id;', {'id': id}).fetchone()
    reviews = db.execute('SELECT * FROM reviews WHERE book_id = :book_id;', {'book_id': id}).fetchall()
    users_review = db.execute('SELECT * FROM reviews WHERE book_id = :book_id AND user_id = :user_id;', {'book_id': id, 'user_id': session['id']}).fetchone()

    goodreads_info = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "U3PyMNiFCwRX3CE0noLqVg", "isbns": "{}".format(book.isbn)}).json()['books'][0]
    print(goodreads_info)
    if request.method == 'GET':
        return render_template('book.html', book=book, reviews=reviews, users_review=users_review, goodreads_info=goodreads_info, user=user)

    if request.method == 'POST':
        if users_review:
            errors.append("You have already sent a review")
        text = request.form['text']
        if not text:
            errors.append("You must write a review first")            
        try:
            rating = int(request.form['rating'])
        except:
            errors.append("You must rate the book first")
        book_id = id
        user_id = session['id']

        if not errors:
            db.execute('INSERT INTO reviews (text, rating, book_id, user_id) VALUES (:text, :rating, :book_id, :user_id)', 
                {'text': text, 'rating': rating, 'book_id': book_id, 'user_id': user_id})
            db.commit()
            users_review = db.execute('SELECT * FROM reviews WHERE book_id = :book_id AND user_id = :user_id;', {'book_id': id, 'user_id': session['id']}).fetchone()
        return render_template('book.html', book=book, reviews=reviews, users_review=users_review, errors=errors, goodreads_info=goodreads_info, user=user)


@app.route("/api/<isbn>", methods=['GET'])
def api(isbn):
    book = db.execute('SELECT * FROM books WHERE isbn = :isbn;', {'isbn': isbn}).fetchone()

    reviews = db.execute('SELECT * FROM reviews WHERE book_id = :book_id;', {'book_id': book.id}).fetchall()
    review_count = len(reviews)
    sum_rating = 0
    for review in reviews:
        sum_rating += review.rating
    try:
        average_rating = sum_rating / review_count
    except ZeroDivisionError:
        average_rating = None
    result = {
        "title": book.title,
        "author": book.author,
        "year": book.year,
        "isbn": book.isbn,
        "review_count": review_count,
        "average_score": average_rating
    }
    return json.dumps(result)

def is_logged_in():
    return 'id' in session.keys()