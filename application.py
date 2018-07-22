import os

from flask import Flask, session, render_template, request, redirect, url_for
from flask_session import Session
from sqlalchemy import or_

from models import db
from models import User, Book, Review

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)




@app.route("/", methods=['GET', 'POST'])
def index():
    if "id" not in session:
        return redirect(url_for('login'))
    if request.method == 'GET':
        return render_template("index.html")
    if request.method == 'POST':
        search_string = request.form['search_string']
        books = Book.query.filter(or_(
            Book.isbn.ilike(f"%{search_string}%"), 
            Book.title.ilike(f"%{search_string}%"), 
            Book.author.ilike(f"%{search_string}%")
            )).all()
        if not books:
            return render_template("index.html", message="No books were found")
        return render_template("search_results.html", books=books)


@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    if request.method == 'POST':
        name = request.form['name']
        login = request.form['login']
        email = request.form['email']
        password = request.form['password']
        # TODO: keep hashed password instead of plain text
        # TODO: user is unique
        user = User(login=login, password=password, name=name, email=email)
        try:
            db.session.add(user)
            db.session.commit()
            return "user saved"
        except Exception as e:
            return "user not saved\n" + str(e)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    if request.method == 'POST':
        login = request.form['login']
        password = request.form['password']
        user = User.query.filter_by(login=login).first()
        if user is not None:
            if user.password == password:
                session['id'] = user.id
                return redirect(url_for('index'))
            else:
                return 'Password doesnt match'
        else:
            return "User not found"


@app.route("/logout", methods=['GET'])
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

    
@app.route("/book/<id>", methods=['GET', 'POST'])
def book(id):
    errors = []
    book = Book.query.get(id)
    reviews = Review.query.filter_by(book_id=id)
    users_review = Review.query.filter_by(book_id = id).filter_by(user_id = session['id']).first()

    if request.method == 'GET':
        return render_template('book.html', book=book, reviews=reviews, users_review=users_review)

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
            review = Review(text=text, rating=rating, book_id=book_id, user_id=user_id)
            db.session.add(review)
            db.session.commit()
            users_review = Review.query.filter_by(book_id = id).filter_by(user_id = session['id']).first()
            
        return render_template('book.html', book=book, reviews=reviews, users_review=users_review, errors=errors)
