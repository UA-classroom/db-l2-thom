import os

import psycopg2
from dotenv import load_dotenv

load_dotenv(override=True)

DATABASE_NAME = os.getenv("DATABASE_NAME")
PASSWORD = os.getenv("PASSWORD")


def get_connection():
    """
    Function that returns a single connection
    In reality, we might use a connection pool, since
    this way we'll start a new connection each time
    someone hits one of our endpoints, which isn't great for performance
    """
    return psycopg2.connect(
        dbname=DATABASE_NAME,
        user="postgres",  # change if needed
        password=PASSWORD,
        host="localhost",  # change if needed
        port="5432",  # change if needed
    )


def create_tables():
    """
    A function to create the necessary tables for the project.
    """
    connection = get_connection()
    
    create_users_table_query = """
    CREATE TABLE IF NOT EXISTS users(
        id                  bigint      GENERATED ALWAYS AS IDENTITY,
        username            varchar(50) UNIQUE NOT NULL, 
        avarar_url          text        UNIQUE,
        user_description    text,
        datetime_joined     timestamptz DEFAULT now()
    );
    """

    with connection:
        with connection.cursor() as cursor:
            cursor.execute(create_users_table_query)


if __name__ == "__main__":
    # Only reason to execute this file would be to create new tables, meaning it serves a migration file
    create_tables()
    print("Tables created successfully.")
