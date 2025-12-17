# Geographical

countries: str = """
CREATE TABLE IF NOT EXISTS countries(
    id      INT             GENERATED ALWAYS AS IDENTITY  PRIMARY KEY,
    name    VARCHAR(100)    UNIQUE  NOT NULL
);
"""

cities: str = """
CREATE TABLE IF NOT EXISTS cities(
    id          INT             GENERATED ALWAYS AS IDENTITY  PRIMARY KEY,
    name        VARCHAR(100)    UNIQUE  NOT NULL,
    country_id  BIGINT  REFERENCES countries(id)
);
"""

geographical_tables: list[str] = [countries, cities]


# Users

users: str = """
CREATE TABLE IF NOT EXISTS users(
    id              BIGINT          GENERATED ALWAYS AS IDENTITY  PRIMARY KEY,
    username        VARCHAR(50)     UNIQUE  NOT NULL, 
    email           VARCHAR(200)    UNIQUE  NOT NULL,
    avatar_url      TEXT            UNIQUE,
    description     VARCHAR(500),
    created_at      TIMESTAMPTZ     DEFAULT now()
);
"""

user_details: str = """
CREATE TABLE IF NOT EXISTS user_details(
    user_id         BIGINT          PRIMARY KEY  REFERENCES users(id),
    first_name      VARCHAR(100),
    last_name       VARCHAR(100),
    phone           INT,
    street_address  VARCHAR(200),
    zip_code        INT,
    city_id         INT             REFERENCES cities(id),
    country_id      INT             REFERENCES countries(id),
    is_company      BOOL            NOT NULL  DEFAULT (false)
);
"""

user_selling_settings: str = """
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

shipping_companies: str = """
CREATE TABLE IF NOT EXISTS shipping_companies(
    id                      BIGINT  GENERATED ALWAYS AS IDENTITY  PRIMARY KEY,
    title                   TEXT    UNIQUE  NOT NULL,
    insurance_information   TEXT    NOT NULL,
    company_logo_url        TEXT    UNIQUE  NOT NULL
);
"""

user_default_shipping_settings: str = """
CREATE TABLE IF NOT EXISTS user_default_shipping_settings(
    user_id                 BIGINT  PRIMARY KEY  REFERENCES users(id),
    shipping_company_id     BIGINT  REFERENCES shipping_companies(id)
);
"""

newsletter_frequency_options: str = """
CREATE TABLE IF NOT EXISTS newsletter_frequency_options(
    id      BIGINT          GENERATED ALWAYS AS IDENTITY  PRIMARY KEY,
    title   VARCHAR(200)    NOT NULL
);
"""

user_email_notification_settings: str = """
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

user_tables: list[str] = [
    users, user_details, user_selling_settings, shipping_companies, user_default_shipping_settings, 
    newsletter_frequency_options, user_email_notification_settings
    ]


# Listings

listing_categories: str = """
CREATE TABLE IF NOT EXISTS listing_categories(
    id                  BIGINT  GENERATED ALWAYS AS IDENTITY  PRIMARY KEY,
    title               TEXT    UNIQUE  NOT NULL,
    description         TEXT,
    main_category_id    BIGINT  REFERENCES listing_categories(id)
);
"""

listing_category_filters: str = """
CREATE TABLE IF NOT EXISTS listing_category_filters(
    id                      BIGINT  GENERATED ALWAYS AS IDENTITY  PRIMARY KEY,
    listing_category_id     BIGINT  REFERENCES listing_categories(id),
    title                   TEXT    NOT NULL
);
"""

listing_types: str = """
CREATE TABLE IF NOT EXISTS listing_types(
    id      BIGINT  GENERATED ALWAYS AS IDENTITY  PRIMARY KEY,
    name    TEXT    NOT NULL
);
"""

listing_statuses: str = """
CREATE TABLE IF NOT EXISTS listing_statuses(
    id      BIGINT  GENERATED ALWAYS AS IDENTITY  PRIMARY KEY,
    title   TEXT    NOT NULL
);
"""

listings: str = """
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

user_saved_listings: str = """
CREATE TABLE IF NOT EXISTS user_saved_listings(
    user_id     BIGINT  REFERENCES users(id),
    listing_id  BIGINT  REFERENCES listings(id),
    PRIMARY KEY (user_id, listing_id)
);
"""

listing_price_suggestions: str = """
CREATE TABLE IF NOT EXISTS listing_price_suggestions(
    listing_id          BIGINT          REFERENCES listings(id)  PRIMARY KEY,
    suggesting_user_id  BIGINT          REFERENCES users(id),
    suggested_price     NUMERIC         NOT NULL,
    suggested_at        TIMESTAMPTZ     DEFAULT now()
);
"""

listing_bids: str = """
CREATE TABLE IF NOT EXISTS listing_bids(
    id          BIGINT          GENERATED ALWAYS AS IDENTITY  PRIMARY KEY,
    user_id     BIGINT          REFERENCES users(id),
    listing_id  BIGINT          REFERENCES listings(id),
    bid_value   NUMERIC         NOT NULL,
    bid_at      TIMESTAMPTZ     DEFAULT now()
);
"""

listing_photos: str = """
CREATE TABLE IF NOT EXISTS listing_photos(
    id          BIGINT       GENERATED ALWAYS AS IDENTITY  PRIMARY KEY,
    listing_id  BIGINT       REFERENCES listings(id),
    url         TEXT         UNIQUE  NOT NULL,
    view_order  BIGINT,
    uploaded_at TIMESTAMPTZ  DEFAULT now()
);
"""

listing_views: str = """
CREATE TABLE IF NOT EXISTS listing_views(
    ip_address  INET            NOT NULL  PRIMARY KEY,
    listing_id  BIGINT          REFERENCES listings(id),
    viewed_at   TIMESTAMPTZ     DEFAULT now()
);
"""

listing_category_filter_options: str = """
CREATE TABLE IF NOT EXISTS listing_category_filter_options(
    id                  BIGINT  GENERATED ALWAYS AS IDENTITY  PRIMARY KEY,
    listing_filter_id   BIGINT  REFERENCES listing_category_filters(id),
    name                TEXT    NOT NULL
);
"""

listing_attributes: str = """
CREATE TABLE IF NOT EXISTS listing_attributes(
    listing_id                  BIGINT  REFERENCES listings(id),
    category_filter_option_id   BIGINT  REFERENCES listing_category_filter_options(id),
    PRIMARY KEY (listing_id, category_filter_option_id)
);
"""

charity_organizations: str = """
CREATE TABLE IF NOT EXISTS charity_organizations(
    id          BIGINT  GENERATED ALWAYS AS IDENTITY  PRIMARY KEY,
    title       TEXT    UNIQUE  NOT NULL,
    logo_url    TEXT    UNIQUE  NOT NULL
);
"""

listing_auction_attributes: str = """
CREATE TABLE IF NOT EXISTS listing_auction_attributes(
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

listing_buynow_attributes: str = """
CREATE TABLE IF NOT EXISTS listing_buynow_attributes(
    listing_id                  BIGINT      REFERENCES listings(id)  PRIMARY KEY,
    price                       NUMERIC     NOT NULL,
    auto_republish              BOOL        NOT NULL  DEFAULT (false),
    storage_location            TEXT,
    charity_id                  BIGINT      REFERENCES charity_organizations(id),
    share_info_upon_donation    BOOL        NOT NULL  DEFAULT (false)
);
"""

product_weight_options: str = """
CREATE TABLE IF NOT EXISTS product_weight_options(
    id      BIGINT  GENERATED ALWAYS AS IDENTITY  PRIMARY KEY,
    weight  BIGINT  UNIQUE  NOT NULL
);
"""

product_size_options: str = """
CREATE TABLE IF NOT EXISTS product_size_options(
    id      BIGINT       GENERATED ALWAYS AS IDENTITY  PRIMARY KEY,
    size    VARCHAR(50)  UNIQUE  NOT NULL
);
"""

shipping_ranges: str = """
CREATE TABLE IF NOT EXISTS shipping_ranges(
    id              BIGINT          GENERATED ALWAYS AS IDENTITY  PRIMARY KEY,
    range_title     VARCHAR(150)    UNIQUE  NOT NULL
);
"""

estimated_shipping_costs: str = """
CREATE TABLE IF NOT EXISTS estimated_shipping_costs(
    shipping_company_id     BIGINT      REFERENCES shipping_companies(id),
    product_weight_id       BIGINT      REFERENCES product_weight_options(id),
    estimated_cost          NUMERIC     NOT NULL,
    PRIMARY KEY (shipping_company_id, product_weight_id)
);
"""

listing_shipping_settings: str = """
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

listing_tables: list[str] = [
    listing_categories, listing_category_filters, listing_types, listing_statuses, 
    listings, user_saved_listings, listing_price_suggestions, listing_bids, 
    listing_photos, listing_views, listing_category_filter_options, listing_attributes, 
    charity_organizations, listing_auction_attributes, listing_buynow_attributes, 
    product_weight_options, product_size_options, shipping_ranges, 
    estimated_shipping_costs, listing_shipping_settings
    ]


# Messages

user_messages: str = """
CREATE TABLE IF NOT EXISTS user_messages(
    id                      BIGINT          GENERATED ALWAYS AS IDENTITY  PRIMARY KEY,
    sender_user_id          BIGINT          REFERENCES users(id),
    listing_id              BIGINT          REFERENCES listings(id),
    body                    TEXT,
    created_at              TIMESTAMPTZ     DEFAULT now(),
    recipient_opened_at     TIMESTAMPTZ
);
"""

user_messages_attachements: str = """
CREATE TABLE IF NOT EXISTS user_messages_attachements(
    user_message_id     BIGINT      REFERENCES user_messages(id)  PRIMARY KEY,
    photo_url           TEXT        UNIQUE  NOT NULL
);
"""

messages_tables: list[str] = [user_messages, user_messages_attachements]


# Ratings

user_ratings: str = """
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

rating_tables: list[str] = [user_ratings]


all_tables_queries: list[str] = [
    countries, cities, users, user_details, user_selling_settings, shipping_companies, 
    user_default_shipping_settings, newsletter_frequency_options, 
    user_email_notification_settings, listing_categories, listing_category_filters, 
    listing_types, listing_statuses, listings, user_saved_listings, 
    listing_price_suggestions, listing_bids, listing_photos, listing_views, 
    listing_category_filter_options, listing_attributes, charity_organizations, 
    listing_auction_attributes, listing_buynow_attributes, product_weight_options, 
    product_size_options, shipping_ranges, estimated_shipping_costs, 
    listing_shipping_settings, user_messages, user_messages_attachements, user_ratings
    ]
