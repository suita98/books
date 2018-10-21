"""This module creates tables in a new database 
and should be executed only once before executing 
module for importing data"""

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

# Establish connection with database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def main():
    db.execute(
        '''CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            login TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            name TEXT NOT NULL
        );
        '''
    )

    db.execute(
        '''CREATE TABLE IF NOT EXISTS books (
            id SERIAL PRIMARY KEY,
            isbn TEXT NOT NULL UNIQUE,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            year TEXT NOT NULL
        );
        '''
    )

    db.execute(
        '''CREATE TABLE IF NOT EXISTS reviews (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            book_id INTEGER NOT NULL,
            text TEXT NOT NULL,
            rating INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (book_id) REFERENCES books (id)
        );
        '''
    )
    db.commit()


if __name__ == "__main__":
    main()