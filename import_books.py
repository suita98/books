import csv
import os

from flask import Flask
from models import db
from models import Book

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

def main():
    f = open("books.csv")
    f.readline()
    reader = csv.reader(f)
    for isbn, title, author, year in reader:
        book = Book(isbn=isbn, title=title, author=author, year=year)
        db.session.add(book)
        print(f"Added: {isbn}, {title}, {author}, {year}")
    db.session.commit()
    print('Done')

if __name__ == "__main__":
    with app.app_context():
        main()