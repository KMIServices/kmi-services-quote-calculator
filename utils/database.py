import os
import json
from datetime import datetime
import pandas as pd
import sqlalchemy
from sqlalchemy import create_engine, text, MetaData, Table, Column, String, Float, Integer, Boolean, DateTime, ForeignKey, select, insert, update
from sqlalchemy.ext.declarative import declarative_base

# Create a base class for declarative class definitions
Base = declarative_base()

# Database connection
def get_db_connection():
    """Create and return a database connection"""
    db_url = os.environ.get('DATABASE_URL')
    
    if not db_url:
        raise ValueError("DATABASE_URL environment variable not set")
    
    # Create engine
    engine = create_engine(db_url)
    return engine

# Define database models
class Quote(Base):
    __tablename__ = 'quotes'
    
    id = Column(Integer, primary_key=True)
    quote_id = Column(String, unique=True, nullable=False)
    timestamp = Column(DateTime, default=datetime.now)
    status = Column(String, default="Quoted")
    admin_created = Column(Boolean, default=False)
    sent_to_customer = Column(Boolean, default=False)
    
    # Customer information
    customer_name = Column(String, nullable=False)
    customer_email = Column(String, nullable=False)
    customer_phone = Column(String, nullable=True)
    customer_address = Column(String, nullable=False)
    customer_postcode = Column(String, nullable=False)
    referral_source = Column(String, nullable=True)
    referral_other = Column(String, nullable=True)
    
    # Property information
    region = Column(String, nullable=False)
    property_size = Column(String, nullable=False)
    num_bathrooms = Column(Integer, nullable=False)
    num_reception_rooms = Column(Integer, nullable=False)
    
    # Service information
    service_type = Column(String, nullable=False)
    cleaning_date = Column(String, nullable=False)
    time_preference = Column(String, nullable=True)
    cleanliness_level = Column(String, default="Normal")
    pet_status = Column(String, default="No Pets")
    cleaner_preference = Column(String, default="No Preference")
    customer_notes = Column(String, nullable=True)
    
    # Additional services
    oven_clean = Column(Boolean, default=False)
    carpet_cleaning = Column(Boolean, default=False)
    carpet_rooms = Column(Integer, default=0)
    internal_windows = Column(Boolean, default=False)
    external_windows = Column(Boolean, default=False)
    balcony_patio = Column(Boolean, default=False)
    cleaning_materials = Column(Boolean, default=False)
    
    # Price details
    base_price = Column(Float, nullable=False)
    extra_bathrooms_cost = Column(Float, default=0)
    extra_reception_cost = Column(Float, default=0)
    additional_services_cost = Column(Float, default=0)
    materials_cost = Column(Float, default=0)
    subtotal = Column(Float, nullable=False)
    markup_percentage = Column(Float, nullable=False)
    markup = Column(Float, nullable=False)
    total_price = Column(Float, nullable=False)
    
    # Business details
    hourly_rate = Column(Float, nullable=False)
    hours_required = Column(Float, nullable=False)
    cleaners_required = Column(Integer, nullable=False)
    region_multiplier = Column(Float, nullable=False)
    
    # Admin adjustments
    admin_notes = Column(String, nullable=True)
    regular_client_discount_percentage = Column(Float, nullable=True)
    regular_client_discount_amount = Column(Float, nullable=True)
    original_price = Column(Float, nullable=True)
    original_cleaners = Column(Integer, nullable=True)
    original_hours = Column(Float, nullable=True)
    original_markup_percentage = Column(Float, nullable=True)
    original_markup = Column(Float, nullable=True)

# Initialize database
def initialize_db():
    """Initialize the database with necessary tables"""
    engine = get_db_connection()
    Base.metadata.create_all(engine)
    return engine

# Convert quote_data to database format
def quote_data_to_db_format(quote_data):
    """Convert the quote_data dictionary to database-compatible format"""
    
    # Extract data from nested structure
    customer_info = quote_data["customer_info"]
    property_info = quote_data["property_info"]
    service_info = quote_data["service_info"]
    additional_services = service_info["additional_services"]
    price_details = quote_data["price_details"]
    
    # Create a flat dictionary for database insertion
    db_data = {
        "quote_id": quote_data.get("quote_id", None),
        "status": quote_data.get("status", "Enquiry"),  # Default to Enquiry for new quotes
        "admin_created": quote_data.get("is_admin_created", False),
        "sent_to_customer": quote_data.get("sent_to_customer", False),
        
        # Customer information
        "customer_name": customer_info["name"],
        "customer_email": customer_info["email"],
        "customer_phone": customer_info.get("phone", None),
        "customer_address": customer_info["address"],
        "customer_postcode": customer_info["postcode"],
        "referral_source": customer_info.get("referral_source", None),
        "referral_other": customer_info.get("referral_other", None),
        
        # Property information
        "region": property_info["region"],
        "property_size": property_info["property_size"],
        "num_bathrooms": property_info["num_bathrooms"],
        "num_reception_rooms": property_info["num_reception_rooms"],
        
        # Service information
        "service_type": service_info["service_type"],
        "cleaning_date": service_info["cleaning_date"],
        "time_preference": service_info.get("time_preference", None),
        "cleanliness_level": service_info.get("cleanliness_level", "Normal"),
        "pet_status": service_info.get("pet_status", "No Pets"),
        "cleaner_preference": service_info.get("cleaner_preference", "No Preference"),
        "customer_notes": service_info.get("customer_notes", None),
        
        # Additional services
        "oven_clean": additional_services["oven_clean"],
        "carpet_cleaning": additional_services["carpet_cleaning"],
        "carpet_rooms": additional_services["carpet_rooms"],
        "internal_windows": additional_services["internal_windows"],
        "external_windows": additional_services["external_windows"],
        "balcony_patio": additional_services["balcony_patio"],
        "cleaning_materials": service_info["cleaning_materials"],
        
        # Price details
        "base_price": price_details["base_price"],
        "extra_bathrooms_cost": price_details["extra_bathrooms_cost"],
        "extra_reception_cost": price_details["extra_reception_cost"],
        "additional_services_cost": price_details["additional_services_cost"],
        "materials_cost": price_details["materials_cost"],
        "subtotal": price_details["subtotal"],
        "markup_percentage": price_details["markup_percentage"],
        "markup": price_details["markup"],
        "total_price": price_details["total_price"],
        
        # Business details
        "hourly_rate": price_details["hourly_rate"],
        "hours_required": price_details["hours_required"],
        "cleaners_required": price_details["cleaners_required"],
        "region_multiplier": price_details["region_multiplier"],
        
        # Admin adjustments (if present)
        "admin_notes": price_details.get("admin_notes", None),
        "regular_client_discount_percentage": price_details.get("regular_client_discount_percentage", None),
        "regular_client_discount_amount": price_details.get("regular_client_discount_amount", None),
        "original_price": price_details.get("original_price", None),
        "original_cleaners": price_details.get("original_cleaners", None),
        "original_hours": price_details.get("original_hours", None),
        "original_markup_percentage": price_details.get("original_markup_percentage", None),
        "original_markup": price_details.get("original_markup", None),
    }
    
    return db_data

# Save quote to database
def save_quote_to_db(quote_data):
    """Save quote data to the database"""
    from utils.data_storage import generate_quote_id
    
    # Initialize database
    engine = initialize_db()
    
    # Generate quote ID if not already present
    if "quote_id" not in quote_data:
        quote_data["quote_id"] = generate_quote_id()
    
    # Convert quote data to database format
    db_data = quote_data_to_db_format(quote_data)
    
    # Create a connection
    with engine.connect() as connection:
        # Check if quote already exists
        result = connection.execute(
            text("SELECT * FROM quotes WHERE quote_id = :quote_id"),
            {"quote_id": db_data["quote_id"]}
        )
        existing_quote = result.fetchone()
        
        if existing_quote:
            # Update existing quote
            stmt = update(Quote).where(Quote.quote_id == db_data["quote_id"]).values(**db_data)
            connection.execute(stmt)
        else:
            # Insert new quote
            stmt = insert(Quote).values(**db_data)
            connection.execute(stmt)
        
        connection.commit()
    
    return quote_data["quote_id"]

# Get all quotes from database
def get_quotes_from_db():
    """Get all quotes from the database and return as a pandas DataFrame"""
    engine = get_db_connection()
    
    try:
        # Query all quotes
        query = "SELECT * FROM quotes ORDER BY timestamp DESC"
        return pd.read_sql(query, engine)
    except Exception as e:
        print(f"Error retrieving quotes from database: {str(e)}")
        return pd.DataFrame()

# Get a specific quote from database
def get_quote_by_id(quote_id):
    """Get a specific quote by ID"""
    engine = get_db_connection()
    
    try:
        query = f"SELECT * FROM quotes WHERE quote_id = '{quote_id}'"
        df = pd.read_sql(query, engine)
        if len(df) > 0:
            # Get the data and provide debug output
            quote_data = df.iloc[0].to_dict()
            print(f"Database returned quote {quote_id} with {len(quote_data)} fields")
            # Check for important fields
            important_fields = ["customer_name", "property_size", "service_type", "total_price"]
            for field in important_fields:
                if field not in quote_data or quote_data[field] is None:
                    print(f"WARNING: Missing or None value for '{field}' in quote {quote_id}")
            
            return quote_data
        print(f"WARNING: No data found for quote {quote_id}")
        return None
    except Exception as e:
        print(f"ERROR retrieving quote {quote_id}: {str(e)}")
        return None

# Update quote status
def update_quote_status(quote_id, status):
    """Update the status of a quote in both database and CSV"""
    # Update in database
    engine = get_db_connection()
    
    with engine.connect() as connection:
        stmt = update(Quote).where(Quote.quote_id == quote_id).values(status=status)
        connection.execute(stmt)
        connection.commit()
    
    # Update in CSV
    try:
        from utils.data_storage import initialize_csv_if_needed
        import pandas as pd
        import os
        
        # Initialize CSV file if it doesn't exist
        initialize_csv_if_needed()
        
        # Get CSV path
        csv_path = os.path.join("data", "quotes.csv")
        
        # Read the CSV file
        df = pd.read_csv(csv_path)
        
        # Find the quote by ID
        if quote_id in df["quote_id"].values:
            df.loc[df["quote_id"] == quote_id, "status"] = status
            df.to_csv(csv_path, index=False)
    except Exception as e:
        print(f"Error updating status in CSV: {str(e)}")
    
    return True

# Update sent_to_customer status
def update_sent_to_customer(quote_id, sent=True):
    """Update the sent_to_customer status of a quote in both database and CSV"""
    from utils.data_storage import update_csv_sent_to_customer
    
    # Update in database
    engine = get_db_connection()
    
    with engine.connect() as connection:
        stmt = update(Quote).where(Quote.quote_id == quote_id).values(sent_to_customer=sent)
        connection.execute(stmt)
        connection.commit()
    
    # Update in CSV
    update_csv_sent_to_customer(quote_id, sent)
    
    return True