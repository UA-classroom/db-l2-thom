import os
import psycopg2
from dotenv import load_dotenv
from create_table_queries import all_tables_queries
from insert_fictive_data_queries import all_fictive_data


load_dotenv(override=True)
DATABASE_NAME = os.getenv("DATABASE_NAME")
PASSWORD = os.getenv("PASSWORD")


def get_connection():
    """
    Function that returns a single connection.
    """
    return psycopg2.connect(
        dbname=DATABASE_NAME,
        user="postgres",
        password=PASSWORD,
        host="localhost",
        port="5432",
    )


def create_tables():
    """
    Function to create the necessary tables for the project.
    """
    connection = get_connection()
    with connection:
        with connection.cursor() as cursor:
            for create_table_query in all_tables_queries:
                cursor.execute(create_table_query)
    if connection:
        connection.close()
    return "Tables created successfully."


def seed_fictive_data():
    """
    Function to fill all tables with some fictive data.
    """
    connection = get_connection()
    with connection:
        with connection.cursor() as cursor:
            for insert_query in all_fictive_data:
                cursor.execute(insert_query)
    if connection:
        connection.close()
    return "Fictive data was inserted successfully."


if __name__ == "__main__":
    print(create_tables())
    # Uncomment below and run to insert fictive data:
    print(seed_fictive_data())        
