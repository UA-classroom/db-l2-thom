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
        id          INT     GENERATED ALWAYS AS IDENTITY  PRIMARY KEY,
        name        TEXT    UNIQUE  NOT NULL,
        country_id  BIGINT  REFERENCES countries(id)
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
        upon_new_device_login               BOOL         NOT NULL  DEFAULT (true),
        copy_read_messages                  BOOL         NOT NULL  DEFAULT (false),
        favorites_list_updates              BOOL         NOT NULL  DEFAULT (true),
        upon_missing_payment                BOOL         NOT NULL  DEFAULT (true),
        upon_failed_auction                 BOOL         NOT NULL  DEFAULT (true),
        upon_bid_exceeding_starting_price   BOOL         NOT NULL  DEFAULT (false),
        other_companies_promotions          BOOL         NOT NULL  DEFAULT (false),
        newsletters                         BOOL         NOT NULL  DEFAULT (false),
        newsletter_frequency_id             BIGINT       NOT NULL  REFERENCES newsletter_frequency_options(id) DEFAULT (1),
        newsletter_frequency_changed_at     TIMESTAMPTZ  NOT NULL  DEFAULT now()
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
        title                   TEXT    NOT NULL
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
        id                  BIGINT          GENERATED ALWAYS AS IDENTITY  PRIMARY KEY,
        created_at          TIMESTAMPTZ     DEFAULT now(),
        title               TEXT            NOT NULL,
        description         TEXT,
        soft_deleted        BOOL            NOT NULL  DEFAULT (false),
        soft_deleted_at     TIMESTAMPTZ     DEFAULT now(),
        pickup_available    BOOL            NOT NULL DEFAULT (false),
        buyer_insurance     BOOL            NOT NULL DEFAULT (true),
        user_id             BIGINT          REFERENCES users(id),
        type_id             BIGINT          REFERENCES listing_types(id),
        status_id           BIGINT          REFERENCES listing_statuses(id),
        category_id         BIGINT          REFERENCES listing_categories(id)
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

    # Messages
    create_user_messages_table_query = """
    CREATE TABLE IF NOT EXISTS user_messages(
        id                      BIGINT          GENERATED ALWAYS AS IDENTITY  PRIMARY KEY,
        sender_user_id          BIGINT          REFERENCES users(id),
        listing_id              BIGINT          REFERENCES listings(id),
        body                    TEXT,
        created_at              TIMESTAMPTZ     DEFAULT now(),
        recipient_opened_at     TIMESTAMPTZ
    );
    """

    create_user_messages_attachements_table_query = """
    CREATE TABLE IF NOT EXISTS user_messages_attachements(
        user_message_id     BIGINT      GENERATED ALWAYS AS IDENTITY  PRIMARY KEY,
        photo_url           TEXT        UNIQUE  NOT NULL
    );
    """

    # Reviewes
    create_user_ratings_table_query = """
    CREATE TABLE IF NOT EXISTS user_ratings(
        listing_id                      BIGINT          REFERENCES listings(id),
        reviewing_user_id               BIGINT          REFERENCES users(id),
        reviewed_at                     TIMESTAMPTZ     DEFAULT now(),
        positive_review                 BOOL            NOT NULL,
        review_comment                  TEXT,
        listing_description_rating      INT,
        listing_communication_rating    INT,
        listing_delivery_time_rating    INT,
        PRIMARY KEY (listing_id, reviewing_user_id)
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
            # Messages
            cursor.execute(create_user_messages_table_query)
            cursor.execute(create_user_messages_attachements_table_query)
            # Reviewes
            cursor.execute(create_user_ratings_table_query)
    
    if connection:
        connection.close()


def seed_data():
    connection = get_connection()

    insert_fictive_country_data_query = """
    INSERT INTO countries(name)
    VALUES
        ('Afghanistan'), ('Albania'), ('Algeria'), ('Andorra'), ('Angola'), ('Antigua and Barbuda'), ('Argentina'), 
        ('Armenia'), ('Australia'), ('Austria'), ('Azerbaijan'), ('Bahamas'), ('Bahrain'), ('Bangladesh'), ('Barbados'), 
        ('Belarus'), ('Belgium'), ('Belize'), ('Benin'), ('Bhutan'), ('Bolivia'), ('Bosnia and Herzegovina'), 
        ('Botswana'), ('Brazil'), ('Brunei'), ('Bulgaria'), ('Burkina Faso'), ('Burundi'), ('Cabo Verde'), 
        ('Cambodia'), ('Cameroon'), ('Canada'), ('Central African Republic'), ('Chad'), ('Chile'), 
        ('China'), ('Colombia'), ('Comoros'), ('Congo'), ('Costa Rica'), ('Croatia'), ('Cuba'), 
        ('Cyprus'), ('Czech Republic'), ('Denmark'), ('Djibouti'), ('Dominica'), ('Dominican Republic'), 
        ('East Timor'), ('Ecuador'), ('Egypt'), ('El Salvador'), ('Equatorial Guinea'), ('Eritrea'), ('Estonia'), 
        ('Eswatini'), ('Ethiopia'), ('Fiji'), ('Finland'), ('France'), ('Gabon'), ('Gambia'), ('Georgia'), 
        ('Germany'), ('Ghana'), ('Greece'), ('Grenada'), ('Guatemala'), ('Guinea'), ('Guinea-Bissau'), ('Guyana'), 
        ('Haiti'), ('Honduras'), ('Hungary'), ('Iceland'), ('India'), ('Indonesia'), ('Iran'), ('Iraq'), ('Ireland'), 
        ('Israel'), ('Italy'), ('Ivory Coast'), ('Jamaica'), ('Japan'), ('Jordan'), ('Kazakhstan'), ('Kenya'), 
        ('Kiribati'), ('South Korea'), ('Kosovo'), ('Kuwait'), ('Kyrgyzstan'), ('Laos'), ('Latvia'), ('Lebanon'), 
        ('Lesotho'), ('Liberia'), ('Libya'), ('Liechtenstein'), ('Lithuania'), ('Luxembourg'), ('Madagascar'), ('Malawi'), 
        ('Malaysia'), ('Maldives'), ('Mali'), ('Malta'), ('Marshall Islands'), ('Mauritania'), ('Mauritius'), 
        ('Mexico'), ('Micronesia'), ('Moldova'), ('Monaco'), ('Mongolia'), ('Montenegro'), ('Morocco'), ('Mozambique'), 
        ('Myanmar'), ('Namibia'), ('Nauru'), ('Nepal'), ('Netherlands'), ('New Zealand'), ('Nicaragua'), ('Niger'), 
        ('Nigeria'), ('North Macedonia'), ('Norway'), ('Oman'), ('Pakistan'), ('Palau'), ('Palestine'), ('Panama'), 
        ('Papua New Guinea'), ('Paraguay'), ('Peru'), ('Philippines'), ('Poland'), ('Portugal'), ('Qatar'), 
        ('Romania'), ('Rwanda'), ('Saint Kitts and Nevis'), ('Saint Lucia'), ('Saint Vincent and the Grenadines'), 
        ('Samoa'), ('San Marino'), ('Sao Tome and Principe'), ('Saudi Arabia'), ('Senegal'), ('Serbia'), ('Seychelles'), 
        ('Sierra Leone'), ('Singapore'), ('Slovakia'), ('Slovenia'), ('Solomon Islands'), ('Somalia'), ('South Africa'), 
        ('South Sudan'), ('Spain'), ('Sri Lanka'), ('Sudan'), ('Suriname'), ('Sweden'), ('Switzerland'), ('Syria'), 
        ('Taiwan'), ('Tajikistan'), ('Tanzania'), ('Thailand'), ('Togo'), ('Tonga'), ('Trinidad and Tobago'), ('Tunisia'), 
        ('Turkey'), ('Turkmenistan'), ('Tuvalu'), ('Uganda'), ('Ukraine'), ('United Arab Emirates'), ('United Kingdom'), 
        ('United States'), ('Uruguay'), ('Uzbekistan'), ('Vanuatu'), ('Vatican City'), ('Venezuela'), ('Vietnam'), ('Yemen'), 
        ('Zambia'), ('Zimbabwe')
    ;
    """

    insert_fictive_city_data_query = """
    INSERT INTO cities(name, country_id)
    VALUES
        ('Borlänge', 137), ('Borås', 137), ('Eskilstuna', 137), ('Falun', 137), ('Gävle', 137), ('Göteborg', 137), 
        ('Halmstad', 137), ('Helsingborg', 137), ('Jönköping', 137), ('Kalmar', 137), ('Karlskrona', 137), ('Karlstad', 137), 
        ('Kristianstad', 137), ('Landskrona', 137), ('Lidingö', 137), ('Linköping', 137), ('Luleå', 137), ('Lund', 137), 
        ('Malmö', 137), ('Motala', 137), ('Norrköping', 137), ('Nyköping', 137), ('Skellefteå', 137), ('Skövde', 137), 
        ('Södertälje', 137), ('Stockholm', 137), ('Sundsvall', 137), ('Trollhättan', 137), ('Tumba', 137), ('Uddevalla', 137), 
        ('Umeå', 137), ('Upplands Väsby', 137), ('Uppsala', 137), ('Varberg', 137), ('Västerås', 137), ('Växjö', 137), 
        ('Åkersberga', 137), ('Örebro', 137), ('Örnsköldsvik', 137), ('Östersund', 137)
    ;
    """

    insert_fictive_users_query = """
    INSERT INTO users(username, avatar_url, description)
    VALUES
        ('MinMax67',            NULL,                               NULL),
        ('Tjorven',             '/server/users/avatars/123.jpg',    NULL),
        ('Melker',              '/server/users/avatars/124.jpg',    'Badar alltid med kläderna på.'),
        ('Jarmo',               NULL,                               'Har aldrig rätt förutom när jag har fel.'),
        ('AnitaParsson',        '/server/users/avatars/125.jpg',    NULL),
        ('CoolBoi_not',         '/server/users/avatars/126.jpg',    'Coolaste katten i stan! :D'),
        ('LisbetSalamander',    '/server/users/avatars/127.jpg',    'Säljer allt och lite till. Fast oftast inget.'),
        ('Martin',              NULL,                               NULL),
        ('Myrorna',             '/server/users/avatars/128.jpg',    'Välkommen till Myrornas webbshop - utrop från 1 kr!')
    ;   
    """

    insert_fictive_user_details_query = """
    INSERT INTO user_details(user_id, first_name, last_name, email, phone, street_address, zip_code, city_id, country_id, is_company)
    VALUES
        (1, 'Maximilian',   NULL,       'max@power.com',            0701231212, NULL,               NULL,   3,  137, false),
        (2, NULL,           NULL,       'tjorven@saltkrakan.se',    0721231213, NULL,               12345,  10, 137, false),
        (3, 'Melker',       NULL,       'melker@saltkrakan.se',     0721231215, NULL,               12365,  10, 137, false),
        (4, NULL,           NULL,       'jarmo_olutta@soumi.fi',    NULL,       NULL,               NULL,   14, 137, false),
        (5, 'Anita',        'Pärsson',  'Panita@telia.se',          0721231217, 'Kostigen 7',       13245,  11, 137, false),
        (6, NULL,           NULL,       'henrik_88@hotmail.com',    NULL,       NULL,               NULL,   13, 137, false),
        (7, 'Lisbet',       'Salander', 'lill-bettan@millenium.nu', 0736737289, 'Mörtstigen 88',    NULL,   17, 137, false),
        (8, NULL,           NULL,       'martin_martin@martin.ma',  NULL,       NULL,               NULL,   4,  137, false),
        (9, 'Myrorna',      NULL,       'info@myrorna.se',          0850356343, 'Hornsgatan 45',    15356,  5,  137, true)
    ;
    """

    insert_fictive_user_selling_settings_query = """
    INSERT INTO user_selling_settings(
	    user_id, auto_review, auto_book_shipping, default_packaging_cost, auto_fill_listing_content, show_listings_fbmarketplace, delayed_delivery_warning
	    )
    VALUES
        (1, true,    DEFAULT, DEFAULT, DEFAULT, DEFAULT, DEFAULT),
        (2, DEFAULT, true,    49.90,   DEFAULT, DEFAULT, DEFAULT),
        (3, DEFAULT, DEFAULT, DEFAULT, DEFAULT, DEFAULT, DEFAULT),
        (4, DEFAULT, DEFAULT, DEFAULT, true,    DEFAULT, DEFAULT),
        (5, DEFAULT, true,    DEFAULT, DEFAULT, DEFAULT, DEFAULT),
        (6, DEFAULT, DEFAULT, DEFAULT, DEFAULT, true,    true),
        (7, DEFAULT, DEFAULT, 100,     DEFAULT, DEFAULT, DEFAULT),
        (8, true,    DEFAULT, DEFAULT, DEFAULT, DEFAULT, DEFAULT),
        (9, DEFAULT, DEFAULT, DEFAULT, DEFAULT, DEFAULT, DEFAULT)
    ;
    """

    insert_fictive_shipping_companies_query = """
    INSERT INTO shipping_companies(title, insurance_information, company_logo_url)
    VALUES
        ('DB Schenker',       'Försäkrad upp till 5 000 kr',       '/server/shipping_companies/logotypes/schenker.png'),
        ('DHL',               'Försäkrad upp till 5 000 kr',       '/server/shipping_companies/logotypes/dhl.png'),
        ('Instabox',          'Ersätter max 150 kr/kg',            '/server/shipping_companies/logotypes/instabox.png'),
        ('PostNord Ombud',    'Ersätter för varor under 5 000 kr', '/server/shipping_companies/logotypes/postnord_ombud.png'),
        ('PostNord Brevlåda', 'Ersätter max 150 kr/kg',            '/server/shipping_companies/logotypes/postnord_brevlada.png')
    ;
    """

    insert_fictive_newsletter_frequency_options_query = """
    INSERT INTO newsletter_frequency_options(title)
    VALUES
        ('Jag vill ta del av samtliga erbjudanden, rabattkoder & rekommendationer'),
        ('Endast 1 gång per vecka'),
        ('Endast 1 gång varannan vecka'),
        ('Endast 1 gång i månaden'),
        ('Pausa alla nyhetsbrev i 3 månader')
    ;
    """

    insert_fictive_newsletter_frequency_options_query = """
    INSERT INTO newsletter_frequency_options(title)
    VALUES
        ('Jag vill ta del av samtliga erbjudanden, rabattkoder & rekommendationer'),
        ('Endast 1 gång per vecka'),
        ('Endast 1 gång varannan vecka'),
        ('Endast 1 gång i månaden'),
        ('Pausa alla nyhetsbrev i 3 månader')
    ;
    """

    insert_user_email_notification_settings_query = """
    INSERT INTO user_email_notification_settings(
        user_id,                 upon_new_device_login,             copy_read_messages,         favorites_list_updates, upon_missing_payment, 
        upon_failed_auction,     upon_bid_exceeding_starting_price, other_companies_promotions, newsletters, 
        newsletter_frequency_id, newsletter_frequency_changed_at
        )
    VALUES
        (1, DEFAULT, false,   false,   false,   false,   false,   DEFAULT, true,    DEFAULT, DEFAULT),
        (2, DEFAULT, DEFAULT, DEFAULT, DEFAULT, DEFAULT, DEFAULT, DEFAULT, DEFAULT, 2,       DEFAULT),
        (3, false,   DEFAULT, true,    DEFAULT, DEFAULT, true,    false,   DEFAULT, 2,       DEFAULT),
        (4, DEFAULT, true,    DEFAULT, DEFAULT, DEFAULT, DEFAULT, DEFAULT, DEFAULT, 3,       DEFAULT),
        (5, DEFAULT, DEFAULT, false,   DEFAULT, false,   DEFAULT, DEFAULT, DEFAULT, DEFAULT, DEFAULT),
        (6, DEFAULT, DEFAULT, DEFAULT, true,    DEFAULT, DEFAULT, DEFAULT, DEFAULT, 4,       DEFAULT),
        (7, true,    DEFAULT, DEFAULT, true,    DEFAULT, DEFAULT, DEFAULT, DEFAULT, DEFAULT, DEFAULT),
        (8, DEFAULT, false,   DEFAULT, DEFAULT, DEFAULT, false,   true,    DEFAULT, 5,       DEFAULT),
        (9, DEFAULT, DEFAULT, DEFAULT, DEFAULT, false,   DEFAULT, DEFAULT, DEFAULT, 5,       DEFAULT)
    ;
    """

    with connection:
        with connection.cursor() as cursor:
            # Geographical
            cursor.execute(insert_fictive_country_data_query)
            cursor.execute(insert_fictive_city_data_query)
            # Users
            cursor.execute(insert_fictive_users_query)
            cursor.execute(insert_fictive_user_details_query)
            cursor.execute(insert_fictive_user_selling_settings_query)
            cursor.execute(insert_fictive_shipping_companies_query)
            cursor.execute(insert_fictive_newsletter_frequency_options_query)
            cursor.execute(insert_user_email_notification_settings_query)
            cursor.execute(insert_fictive_newsletter_frequency_options_query)
    
    if connection:
        connection.close()


if __name__ == "__main__":
    # Only reason to execute this file would be to create new tables, meaning it serves a migration file
    create_tables()
    print("Tables created successfully.")
    seed_data()
    print("Fictive data was inserted successfully.")
    
