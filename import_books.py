"""This module imports books into books table 
and should be executed after executing module 
that creates tables"""

import os
import csv

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

# Establish connection with database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def main():
    f = open("books.csv")
    f.readline()
    reader = csv.reader(f)
    for isbn, title, author, year in reader:
        db.execute('INSERT INTO books (isbn, title, author, year) VALUES (:isbn, :title, :author, :year);', 
        {'isbn': isbn, 'title': title, 'author': author, 'year': year})
        print(f"Added: {isbn}, {title}, {author}, {year}")
    db.commit()
    print('Done')

if __name__ == "__main__":
    main()
