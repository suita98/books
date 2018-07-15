import os

from flask import Flask, session, render_template, request, redirect, url_for
from flask_session import Session

from models import db
from models import User

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




@app.route("/")
def index():
    if "username" not in session:
        return redirect(url_for('login'))
    else:
        return render_template("index.html")


@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    else:
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
    else:
        login = request.form['login']
        password = request.form['password']
        user = User.query.filter_by(login=login).first()
        if user is not None:
            if user.password == password:
                session['username'] = login
                return redirect(url_for('index'))
            else:
                return 'Password doesnt match'
        else:
            return "User not found"


@app.route("/logout", methods=['GET'])
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))
