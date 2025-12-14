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
    
    # Geographical
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

    # Users
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

    create_user_selling_settings_table_query = """
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

    create_user_default_shipping_settings_table_query = """
    CREATE TABLE IF NOT EXISTS user_default_shipping_settings(
        user_id                 BIGINT  PRIMARY KEY  REFERENCES users(id),
        shipping_company_id     BIGINT  REFERENCES shipping_companies(id)
    );
    """

    create_newsletter_frequency_options_table_query = """
    CREATE TABLE IF NOT EXISTS newsletter_frequency_options(
        id      BIGINT  GENERATED ALWAYS AS IDENTITY  PRIMARY KEY,
        title   TEXT    NOT NULL
    );
    """

    create_user_email_notification_settings_table_query = """
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

    # Listings
    create_listing_categories_table_query = """
    CREATE TABLE IF NOT EXISTS listing_categories(
        id                  BIGINT  GENERATED ALWAYS AS IDENTITY  PRIMARY KEY,
        title               TEXT    UNIQUE  NOT NULL,
        description         TEXT,
        main_category_id    BIGINT  REFERENCES listing_categories(id)
    );
    """

    create_listing_category_filters_table_query = """
    CREATE TABLE IF NOT EXISTS listing_category_filters(
        id                      BIGINT  GENERATED ALWAYS AS IDENTITY  PRIMARY KEY,
        listing_category_id     BIGINT  REFERENCES listing_categories(id),
        title   TEXT            NOT NULL
    );
    """

    create_listing_types_table_query = """
    CREATE TABLE IF NOT EXISTS listing_types(
        id      BIGINT  GENERATED ALWAYS AS IDENTITY  PRIMARY KEY,
        name    TEXT    NOT NULL
    );
    """

    create_listing_statuses_table_query = """
    CREATE TABLE IF NOT EXISTS listing_statuses(
        id      BIGINT  GENERATED ALWAYS AS IDENTITY  PRIMARY KEY,
        title   TEXT    NOT NULL
    );
    """

    create_listings_table_query = """
    CREATE TABLE IF NOT EXISTS listings(
        id          BIGINT          GENERATED ALWAYS AS IDENTITY  PRIMARY KEY,
        created_at  TIMESTAMPTZ     DEFAULT now(),
        title       TEXT            NOT NULL,
        description TEXT,
        soft_deleted    BOOL    NOT NULL  DEFAULT (false),
        soft_deleted_at TIMESTAMPTZ DEFAULT now(),
        pickup_available    BOOL    NOT NULL DEFAULT (false),
        buyer_insurance     BOOL    NOT NULL DEFAULT (true),
        user_id             BIGINT  REFERENCES users(id),
        type_id             BIGINT  REFERENCES listing_types(id),
        status_id           BIGINT  REFERENCES listing_statuses(id),
        category_id         BIGINT  REFERENCES listing_categories(id)
    );
    """

    create_user_saved_listings_table_query = """
    CREATE TABLE IF NOT EXISTS user_saved_listings(
        user_id     BIGINT  REFERENCES users(id),
        listing_id  BIGINT  REFERENCES listings(id),
        PRIMARY KEY (user_id, listing_id)
    );
    """

    create_listing_price_suggestions_table_query = """
    CREATE TABLE IF NOT EXISTS listing_price_suggestions(
        listing_id          BIGINT          REFERENCES listings(id)  PRIMARY KEY,
        suggesting_user_id  BIGINT          REFERENCES users(id),
        suggested_price     NUMERIC         NOT NULL,
        suggested_at        TIMESTAMPTZ     DEFAULT now()
    );
    """

    create_listing_bids_table_query = """
    CREATE TABLE IF NOT EXISTS listing_bids(
        id          BIGINT          GENERATED ALWAYS AS IDENTITY  PRIMARY KEY,
        user_id     BIGINT          REFERENCES users(id),
        listing_id  BIGINT          REFERENCES listings(id),
        bid_value   NUMERIC         NOT NULL,
        bid_at      TIMESTAMPTZ     DEFAULT now()
    );
    """

    create_listing_photos_table_query = """
    CREATE TABLE IF NOT EXISTS listing_photos(
        id          BIGINT  GENERATED ALWAYS AS IDENTITY  PRIMARY KEY,
        listing_id  BIGINT  REFERENCES listings(id),
        url         TEXT    UNIQUE  NOT NULL,
        view_order  BIGINT
    );
    """

    create_listing_views_table_query = """
    CREATE TABLE IF NOT EXISTS listing_views(
        ip_address  INET            NOT NULL  PRIMARY KEY,
        listing_id  BIGINT          REFERENCES listings(id),
        viewed_at   TIMESTAMPTZ     DEFAULT now()
    );
    """

    create_listing_category_filter_options_table_query = """
    CREATE TABLE IF NOT EXISTS listing_category_filter_options(
        id                  BIGINT  GENERATED ALWAYS AS IDENTITY  PRIMARY KEY,
        listing_filter_id   BIGINT  REFERENCES listing_category_filters(id),
        name                TEXT    NOT NULL
    );
    """

    create_listing_attributes_table_query = """
    CREATE TABLE IF NOT EXISTS listing_attributes(
        listing_id                  BIGINT  REFERENCES listings(id),
        category_filter_option_id   BIGINT  REFERENCES listing_category_filter_options(id),
        PRIMARY KEY (listing_id, category_filter_option_id)
    );
    """

    create_charity_organizations_table_query = """
    CREATE TABLE IF NOT EXISTS charity_organizations(
        id          BIGINT  GENERATED ALWAYS AS IDENTITY  PRIMARY KEY,
        title       TEXT    UNIQUE  NOT NULL,
        logo_url    TEXT    UNIQUE  NOT NULL
    );
    """

    create_listing_auction_attributes_table_query = """
    CREATE TABLE IF NOT EXISTS listing_attributes(
        listing_id                  BIGINT          REFERENCES listings(id)  PRIMARY KEY,
        starting_price              NUMERIC         NOT NULL,
        auction_deadline_datetime   TIMESTAMPTZ     NOT NULL,
        auto_republish              BOOL            NOT NULL  DEFAULT (false),
        minimum_price               NUMERIC,
        storage_location            TEXT,
        charity_id                  BIGINT          REFERENCES charity_organizations(id),
        share_info_upon_donation    BOOL            NOT NULL  DEFAULT (false)
    );
    """

    create_listing_buynow_attributes_table_query = """
    CREATE TABLE IF NOT EXISTS listing_buynow_attributes(
        listing_id                  BIGINT      REFERENCES listings(id)  PRIMARY KEY,
        price                       NUMERIC     NOT NULL,
        auto_republish              BOOL        NOT NULL  DEFAULT (false),
        storage_location            TEXT,
        charity_id                  BIGINT      REFERENCES charity_organizations(id),
        share_info_upon_donation    BOOL        NOT NULL  DEFAULT (false)
    );
    """

    create_product_weight_options_table_query = """
    CREATE TABLE IF NOT EXISTS product_weight_options(
        id      BIGINT  GENERATED ALWAYS AS IDENTITY  PRIMARY KEY,
        weight  BIGINT  UNIQUE  NOT NULL
    );
    """

    create_product_size_options_table_query = """
    CREATE TABLE IF NOT EXISTS product_size_options(
        id      BIGINT  GENERATED ALWAYS AS IDENTITY  PRIMARY KEY,
        size    BIGINT  UNIQUE  NOT NULL
    );
    """
    
    create_shipping_ranges_table_query = """
    CREATE TABLE IF NOT EXISTS shipping_ranges(
        id              BIGINT  GENERATED ALWAYS AS IDENTITY  PRIMARY KEY,
        range_title     BIGINT  UNIQUE  NOT NULL
    );
    """

    create_estimated_shipping_costs_table_query = """
    CREATE TABLE IF NOT EXISTS estimated_shipping_costs(
        shipping_company_id     BIGINT      REFERENCES shipping_companies(id),
        product_weight_id       BIGINT      REFERENCES product_weight_options(id),
        estimated_cost          NUMERIC     NOT NULL,
        PRIMARY KEY (shipping_company_id, product_weight_id)
    );
    """

    create_listing_shipping_settings_table_query = """
    CREATE TABLE IF NOT EXISTS listing_shipping_settings(
        listing_id              BIGINT      REFERENCES listings(id)  PRIMARY KEY,
        shipping_company_id     BIGINT      REFERENCES shipping_companies(id),
        user_shipping_cost      NUMERIC,
        packaging_fee           NUMERIC,
        product_weight_id       BIGINT      REFERENCES product_weight_options(id),
        product_size_id         BIGINT      REFERENCES product_size_options(id),
        shipping_range_id       BIGINT      REFERENCES shipping_ranges(id)
    );
    """

    with connection:
        with connection.cursor() as cursor:
            # Geographical
            cursor.execute(create_countries_table_query)
            cursor.execute(create_cities_table_query)
            # Users
            cursor.execute(create_users_table_query)
            cursor.execute(create_user_details_table_query)
            cursor.execute(create_user_selling_settings_table_query)
            cursor.execute(create_shipping_companies_table_query)
            cursor.execute(create_user_default_shipping_settings_table_query)
            cursor.execute(create_newsletter_frequency_options_table_query)
            cursor.execute(create_user_email_notification_settings_table_query)
            # Listings
            cursor.execute(create_listing_categories_table_query)
            cursor.execute(create_listing_category_filters_table_query)
            cursor.execute(create_listing_types_table_query)
            cursor.execute(create_listing_statuses_table_query)
            cursor.execute(create_listings_table_query)
            cursor.execute(create_user_saved_listings_table_query)
            cursor.execute(create_listing_price_suggestions_table_query)
            cursor.execute(create_listing_bids_table_query)
            cursor.execute(create_listing_photos_table_query)
            cursor.execute(create_listing_views_table_query)
            cursor.execute(create_listing_category_filter_options_table_query)
            cursor.execute(create_listing_attributes_table_query)
            cursor.execute(create_charity_organizations_table_query)
            cursor.execute(create_listing_auction_attributes_table_query)
            cursor.execute(create_listing_buynow_attributes_table_query)
            cursor.execute(create_product_weight_options_table_query)
            cursor.execute(create_product_size_options_table_query)
            cursor.execute(create_shipping_ranges_table_query)
            cursor.execute(create_estimated_shipping_costs_table_query)
            cursor.execute(create_listing_shipping_settings_table_query)


if __name__ == "__main__":
    # Only reason to execute this file would be to create new tables, meaning it serves a migration file
    create_tables()
    print("Tables created successfully.")
