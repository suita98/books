import os

from flask import Flask, session, render_template, request
# from flask_session import Session

from models import db
from models import User

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)


@app.route("/")
def index():
    return "Project 1: TODO"


@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        login = request.form['login']
        email = request.form['email']
        password = request.form['password']
        user = User(login=login, password=password, name=name, email=email)
        try:
            db.session.add(user)
            db.session.commit()
            return "user saved"
        except Exception as e:
            return "user not saved\n" + str(e)
    else:
        return render_template('register.html')

@app.route("/login", methods=['GET', 'POST'])
def login():
    return render_template('login.html')