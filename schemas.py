from datetime import date
from pydantic import BaseModel, Field, EmailStr

# Geographical
class CountryCreate(BaseModel):
    name: str = Field(..., max_length=70)

class CityCreate(BaseModel):
    name: str = Field(..., max_length=70)
    country_id: int = Field(..., )


# Users
class UserCreate(BaseModel):
    username: str = Field(..., max_length=50)
    email: EmailStr = Field(..., max_length=200)

class UserDetailsCreate(BaseModel):
    user_id: int = Field(...,)
    first_name: str = Field(max_length=100)
    last_name: str = Field(max_length=100)
    phone: int
    street_address: str
    zip_code: int
    city_id: int
    country_id: int
    is_company: bool

class NewsletterFrequencyOptionCreate(BaseModel):
    title: str = Field(..., max_length=200)

class UserNotificationSettingsCreate(BaseModel):
    user_id: int
    upon_new_device_login: bool
    copy_read_messages: bool
    favorites_list_updates: bool
    upon_missing_payment: bool
    upon_failed_auction: bool
    upon_bid_exceeding_starting_price: bool
    other_companies_promotions: bool
    newsletters: bool
    newsletter_frequency_id: int


    