import os
import psycopg2

from db_setup import get_connection
from fastapi import FastAPI, HTTPException, status
from psycopg2.extras import RealDictCursor
from schemas import CountryCreate, CityCreate, UserCreate, UserDetailsCreate, UserNotificationSettingsCreate, NewsletterFrequencyOptionCreate


app = FastAPI()

# Detail endpoints
@app.get("/user/{id}")
def get_user(id: int):
    connection = get_connection()
    with connection:
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""SELECT * FROM users
                           WHERE id = %s;""", (id,))
            result = cursor.fetchone()
            if not result:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
            return result

@app.get("/users")
def list_users(limit: int = 25):
    connection = get_connection()
    with connection:
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""SELECT * FROM users 
                           LIMIT %s;""", (limit,))
            result = cursor.fetchall()
            if not result:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Users not found")
            return result

@app.get("/user/{id}/newsletter_frequency")
def get_user_newsletter_frequency_choice(id: int):
    connection = get_connection()
    with connection:
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""SELECT user_id, id, title
                              FROM newsletter_frequency_options
                              INNER JOIN user_email_notification_settings
                              ON newsletter_frequency_options.id = user_email_notification_settings.newsletter_frequency_id
                              WHERE user_id = %s;""", (id,))
            result = cursor.fetchone()
            if not result:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
            return result

@app.get("/listing/{id}")
def get_listing(id: int):
    connection = get_connection()
    with connection:
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""SELECT * FROM listings 
                           WHERE id = %s;""", (id,))
            result = cursor.fetchall()
            if not result:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Listing not found")
            return result

@app.get("/listing/{id}/photos")
def get_listing_photos(id: int):
    connection = get_connection()
    with connection:
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""SELECT * FROM listing_photos 
                           WHERE listing_id = %s;""", (id,))
            result = cursor.fetchall()
            if not result:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Photos not found")
            return result

@app.get("/listings/photos")
def list_listing_photos():
    connection = get_connection()
    with connection:
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""SELECT * FROM listing_photos;""")
            result = cursor.fetchall()
            if not result:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Photos not found")
            return result

@app.get("/listings")
def list_listings(limit: int = 25):
    connection = get_connection()
    with connection:
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""SELECT * FROM listings 
                           LIMIT %s;""", (limit,))
            result = cursor.fetchall()
            if not result:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Listings not found")
            return result

@app.get("/user/{user_id}/recieved-ratings")
def get_received_ratings(user_id: int):
    connection = get_connection()
    with connection:
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                           SELECT user_id, listing_id, reviewing_user_id, reviewed_at, 
                                  positive_review, review_comment, listing_description_rating, 
                                  listing_communication_rating, listing_delivery_time_rating
                           FROM listings
                           INNER JOIN user_ratings
                           ON listings.id = user_ratings.listing_id
                           WHERE user_id = %s;
                           """, (user_id,))
            result = cursor.fetchall()
            if not result:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ratings not found")
            return result

@app.get("/user/{id}/provided-ratings")
def get_provided_ratings(user_id: int):
    connection = get_connection()
    with connection:
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                           SELECT * 
                           FROM user_ratings
                           WHERE reviewing_user_id = %s;
                           """, (user_id,))
            result = cursor.fetchone()
            if not result:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ratings not found")
            return result

@app.get("/ratings")
def list_ratings(limit: int = 25):
    connection = get_connection()
    with connection:
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""SELECT * FROM user_ratings 
                              LIMIT %s;""", (limit,))
            result = cursor.fetchall()
            if not result:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ratings not found")
            return result



# Delete endpoints
@app.delete("/listing/photos/{id}")
def delete_listing_photo(id: int):
    connection = get_connection()
    with connection:
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""DELETE FROM listing_photos 
                              WHERE id = %s
                              RETURNING id;""", (id,))
            result = cursor.fetchone()
            if not result:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found")
            return {"message": f"Photo with ID {id} was deleted."}


# Post endpoints
@app.post("/countries")
def create_country(country_input: CountryCreate):
    """Create a new country in the 'countries' table.
    Returns the newly created country object with its id."""
    with get_connection() as connection:
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            try:
                cursor.execute("""
                               INSERT INTO countries(name)
                               VALUES (%s)
                               RETURNING id;
                               """, (country_input.name,)
                               )
                inserted = cursor.fetchone()
            except psycopg2.errors.UniqueViolation:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Country already exists")
    return {
        "id": inserted["id"],
        "name": country_input.name
    }

@app.post("/cities")
def create_city(city_input: CityCreate):
    """Create a new city in the 'cities' table.
    Returns the newly created city object with its id."""
    with get_connection() as connection:
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            try:
                cursor.execute("""
                               INSERT INTO cities(name, country_id)
                               VALUES (%s, %s)
                               RETURNING id;
                               """, (city_input.name, city_input.country_id)
                               )
                inserted = cursor.fetchone()
            except psycopg2.errors.UniqueViolation:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="City already exists")
    return {
        "id": inserted["id"],
        "name": city_input.name,
        "country_id": city_input.country_id
    }

@app.post("/users")
def create_user(user_input: UserCreate):
    """Create a new user in the 'users' table.
    Returns the newly created user object with its id."""
    with get_connection() as connection:
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            try:
                cursor.execute("""
                               INSERT INTO users(username, email)
                               VALUES (%s, %s)
                               RETURNING id;
                               """, (user_input.username, user_input.email)
                               )
                inserted = cursor.fetchone()
            except psycopg2.errors.UniqueViolation:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists")
    return {
        "id": inserted["id"],
        "username": user_input.username,
        "email": user_input.email
    }

@app.post("/user_details")
def create_user_details(user_details_input: UserDetailsCreate):
    """Create new user details in the 'user_details' table.
    Returns the newly created user_details object."""
    with get_connection() as connection:
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            try:
                cursor.execute("""
                               INSERT INTO user_details(
                                   user_id, first_name, last_name, phone, 
                                   street_address, zip_code, city_id, 
                                   country_id, is_company
                               )
                               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                               ;
                               """, (user_details_input.user_id, 
                                     user_details_input.first_name, 
                                     user_details_input.last_name, 
                                     user_details_input.phone, 
                                     user_details_input.street_address, 
                                     user_details_input.zip_code, 
                                     user_details_input.city_id, 
                                     user_details_input.country_id, 
                                     user_details_input.is_company
                                     )
                               )
            except psycopg2.errors.UniqueViolation:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User doesn't exists")
    return {
        "user_id": user_details_input.user_id,
        "first_name": user_details_input.first_name,
        "last_name": user_details_input.last_name,
        "phone": user_details_input.phone,
        "street_address": user_details_input.street_address,
        "zip_code": user_details_input.zip_code,
        "city_id": user_details_input.city_id,
        "country_id": user_details_input.country_id,
        "is_company": user_details_input.is_company
    }

@app.post("/newsletter_frequency_options")
def create_newsletter_frequency_options(newsletter_frequency_options_input: NewsletterFrequencyOptionCreate):
    """Create a new newsletter frequency option in the 'newsletter_frequency_options' table.
    Returns the newly created newsletter frequency option object with its id."""
    with get_connection() as connection:
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            try:
                cursor.execute("""
                               INSERT INTO newsletter_frequency_options(title)
                               VALUES (%s)
                               RETURNING id;
                               """, (newsletter_frequency_options_input.title,)
                               )
                inserted = cursor.fetchone()
            except psycopg2.errors.UniqueViolation:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Option already exists")
    return {
        "id": inserted["id"],
        "title": newsletter_frequency_options_input.title
    }

@app.post("/user_notification_settings")
def create_user_notification_settings(user_notification_settings_input: UserNotificationSettingsCreate):
    """Create new user notification_settings in the 'user_email_notification_settings' table.
    Returns the newly created user_email_notification_settings object."""
    with get_connection() as connection:
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            try:
                cursor.execute("""
                               INSERT INTO user_email_notification_settings(
                                   user_id, upon_new_device_login, 
                                   copy_read_messages, favorites_list_updates, 
                                   upon_missing_payment, upon_failed_auction, 
                                   upon_bid_exceeding_starting_price, 
                                   other_companies_promotions, newsletters, 
                                   newsletter_frequency_id
                               )
                               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                               ;
                               """, (user_notification_settings_input.user_id,
                                     user_notification_settings_input.upon_new_device_login,
                                     user_notification_settings_input.copy_read_messages,
                                     user_notification_settings_input.favorites_list_updates,
                                     user_notification_settings_input.upon_missing_payment,
                                     user_notification_settings_input.upon_failed_auction,
                                     user_notification_settings_input.upon_bid_exceeding_starting_price,
                                     user_notification_settings_input.other_companies_promotions,
                                     user_notification_settings_input.newsletters,
                                     user_notification_settings_input.newsletter_frequency_id
                                     )
                               )
            except psycopg2.errors.UniqueViolation:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists")
    return {
        "user_id": user_notification_settings_input.user_id,
        "upon_new_device_login": user_notification_settings_input.upon_new_device_login,
        "copy_read_messages": user_notification_settings_input.copy_read_messages,
        "favorites_list_updates": user_notification_settings_input.favorites_list_updates,
        "upon_missing_payment": user_notification_settings_input.upon_missing_payment,
        "upon_failed_auction": user_notification_settings_input.upon_failed_auction,
        "upon_bid_exceeding_starting_price": user_notification_settings_input.upon_bid_exceeding_starting_price,
        "other_companies_promotions": user_notification_settings_input.other_companies_promotions,
        "newsletters": user_notification_settings_input.newsletters,
        "newsletter_frequency_id": user_notification_settings_input.newsletter_frequency_id
    }