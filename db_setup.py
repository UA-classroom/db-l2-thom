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
    
    create_countries_table_query = """
    CREATE TABLE IF NOT EXISTS countries(
        id      INT     GENERATED ALWAYS AS IDENTITY  PRIMARY KEY,
        name    TEXT    UNIQUE  NOT NULL
    );
    """

    create_cities_table_query = """
    CREATE TABLE IF NOT EXISTS cities(
        id      INT     GENERATED ALWAYS AS IDENTITY  PRIMARY KEY,
        name    TEXT    UNIQUE  NOT NULL
    );
    """

    create_users_table_query = """
    CREATE TABLE IF NOT EXISTS users(
        id              BIGINT          GENERATED ALWAYS AS IDENTITY  PRIMARY KEY,
        username        VARCHAR(50)     UNIQUE  NOT NULL, 
        avatar_url      TEXT            UNIQUE,
        description     TEXT,
        created_at      TIMESTAMPTZ     DEFAULT now()
    );
    """

    create_user_details_table_query = """
    CREATE TABLE IF NOT EXISTS user_details(
        user_id         BIGINT  PRIMARY KEY  REFERENCES users(id),
        first_name      TEXT,
        last_name       TEXT,
        email           TEXT    UNIQUE  NOT NULL,
        phone           INT,
        street_address  TEXT,
        zip_code        INT,
        city_id         INT     REFERENCES cities(id),
        country_id      INT     REFERENCES countries(id),
        is_company      BOOL    NOT NULL  DEFAULT (false)
    );
    """

    create_user_selling_settings = """
    CREATE TABLE IF NOT EXISTS user_selling_settings(
        user_id                     BIGINT      PRIMARY KEY  REFERENCES users(id),
        auto_review                 BOOL        NOT NULL  DEFAULT (false),
        auto_book_shipping          BOOL        NOT NULL  DEFAULT (false), 
        default_packaging_cost      NUMERIC,
        auto_fill_listing_content   BOOL        NOT NULL  DEFAULT (false),
        show_listings_fbmarketplace BOOL        NOT NULL  DEFAULT (false),
        delayed_delivery_warning    BOOL        NOT NULL  DEFAULT (false)
    );
    """

    create_shipping_companies_table_query = """
    CREATE TABLE IF NOT EXISTS shipping_companies(
        id                      BIGINT  GENERATED ALWAYS AS IDENTITY  PRIMARY KEY,
        title                   TEXT    UNIQUE  NOT NULL,
        insurance_information   TEXT    NOT NULL,
        company_logo_url        TEXT    UNIQUE  NOT NULL
    );
    """

    create_user_default_shipping_settings = """
    CREATE TABLE IF NOT EXISTS user_default_shipping_settings(
        user_id                 BIGINT  PRIMARY KEY  REFERENCES users(id),
        shipping_company_id     BIGINT  REFERENCES shipping_companies(id)
    );
    """

    create_newsletter_frequency_options = """
    CREATE TABLE IF NOT EXISTS newsletter_frequency_options(
        id      BIGINT  GENERATED ALWAYS AS IDENTITY  PRIMARY KEY,
        title   TEXT    NOT NULL
    );
    """

    create_user_email_notification_settings = """
    CREATE TABLE IF NOT EXISTS user_email_notification_settings(
        user_id                             BIGINT  PRIMARY KEY  REFERENCES users(id),
        upon_new_device_login               BOOL    NOT NULL  DEFAULT (true),
        copy_read_messages                  BOOL    NOT NULL  DEFAULT (false),
        favorites_list_updates              BOOL    NOT NULL  DEFAULT (true),
        upon_missing_payment                BOOL    NOT NULL  DEFAULT (true),
        upon_failed_auction                 BOOL    NOT NULL  DEFAULT (true),
        upon_bid_exceeding_starting_price   BOOL    NOT NULL  DEFAULT (false),
        other_companies_promotions          BOOL    NOT NULL  DEFAULT (false),
        newsletters                         BOOL    NOT NULL  DEFAULT (false),
        newsletter_frequency_id             BIGINT  NOT NULL  REFERENCES newsletter_frequency_options(id)
    );
    """


    with connection:
        with connection.cursor() as cursor:
            cursor.execute(create_countries_table_query)
            cursor.execute(create_cities_table_query)
            cursor.execute(create_users_table_query)
            cursor.execute(create_user_details_table_query)
            cursor.execute(create_user_selling_settings)
            cursor.execute(create_shipping_companies_table_query)
            cursor.execute(create_user_default_shipping_settings)
            cursor.execute(create_newsletter_frequency_options)
            cursor.execute(create_user_email_notification_settings)


if __name__ == "__main__":
    # Only reason to execute this file would be to create new tables, meaning it serves a migration file
    create_tables()
    print("Tables created successfully.")
