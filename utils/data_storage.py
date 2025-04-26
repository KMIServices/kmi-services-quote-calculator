import os
import csv
import time
import datetime
import pandas as pd

def initialize_csv_if_needed():
    """Create the quotes CSV file with headers if it doesn't exist"""
    data_dir = os.path.join("data")
    os.makedirs(data_dir, exist_ok=True)
    
    csv_path = os.path.join(data_dir, "quotes.csv")
    
    if not os.path.exists(csv_path):
        # Define CSV headers
        headers = [
            "quote_id", "timestamp", "status", "admin_created", "sent_to_customer",
            "customer_name", "customer_email", "customer_phone", "customer_address", "customer_postcode",
            "referral_source", "referral_other",
            "region", "property_size", "num_bathrooms", "num_reception_rooms",
            "service_type", "cleaning_date", "time_preference", "cleanliness_level", "pet_status", "cleaner_preference", "customer_notes",
            "oven_clean", "carpet_cleaning", "carpet_rooms", "internal_windows", "external_windows", "balcony_patio", "cleaning_materials",
            "base_price", "extra_bathrooms_cost", "extra_reception_cost", "additional_services_cost", "materials_cost",
            "subtotal", "markup_percentage", "markup", "total_price",
            "hourly_rate", "hours_required", "cleaners_required", "region_multiplier",
            "admin_notes", "regular_client_discount_percentage", "regular_client_discount_amount", 
            "original_price", "original_cleaners", "original_hours", "original_markup_percentage", "original_markup"
        ]
        
        # Create CSV file with headers
        with open(csv_path, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(headers)

def generate_quote_id():
    """Generate a unique quote ID based on current timestamp"""
    timestamp = int(time.time())
    return f"Q{timestamp}"

def save_quote_to_csv(quote_data):
    """Save quote data to CSV file and return the quote_id"""
    # Initialize CSV file if it doesn't exist
    initialize_csv_if_needed()
    
    # Generate a unique quote ID if not already present
    if "quote_id" not in quote_data:
        quote_data["quote_id"] = generate_quote_id()
    
    # Store quote_id for return
    quote_id = quote_data["quote_id"]
    
    # Set default status if not present
    if "status" not in quote_data:
        quote_data["status"] = "Quoted"
    
    # Get CSV path
    csv_path = os.path.join("data", "quotes.csv")
    
    # Extract data from nested structure
    customer_info = quote_data["customer_info"]
    property_info = quote_data["property_info"]
    service_info = quote_data["service_info"]
    additional_services = service_info["additional_services"]
    price_details = quote_data["price_details"]
    
    # Create a flat row for CSV
    row = [
        quote_data["quote_id"],
        datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        quote_data["status"],
        quote_data.get("admin_created", False),
        quote_data.get("sent_to_customer", False),
        
        # Customer information
        customer_info["name"],
        customer_info["email"],
        customer_info.get("phone", ""),
        customer_info["address"],
        customer_info["postcode"],
        customer_info.get("referral_source", ""),
        customer_info.get("referral_other", ""),
        
        # Property information
        property_info["region"],
        property_info["property_size"],
        property_info["num_bathrooms"],
        property_info["num_reception_rooms"],
        
        # Service information
        service_info["service_type"],
        service_info["cleaning_date"],
        service_info.get("time_preference", ""),
        service_info.get("cleanliness_level", "Normal"),
        service_info.get("pet_status", "No Pets"),
        service_info.get("cleaner_preference", "No Preference"),
        service_info.get("customer_notes", ""),
        
        # Additional services
        additional_services["oven_clean"],
        additional_services["carpet_cleaning"],
        additional_services["carpet_rooms"],
        additional_services["internal_windows"],
        additional_services["external_windows"],
        additional_services["balcony_patio"],
        service_info["cleaning_materials"],
        
        # Price details
        price_details["base_price"],
        price_details["extra_bathrooms_cost"],
        price_details["extra_reception_cost"],
        price_details["additional_services_cost"],
        price_details["materials_cost"],
        price_details["subtotal"],
        price_details["markup_percentage"],
        price_details["markup"],
        price_details["total_price"],
        
        # Business details
        price_details["hourly_rate"],
        price_details["hours_required"],
        price_details["cleaners_required"],
        price_details["region_multiplier"],
        
        # Admin adjustments (if present)
        price_details.get("admin_notes", ""),
        price_details.get("regular_client_discount_percentage", ""),
        price_details.get("regular_client_discount_amount", ""),
        price_details.get("original_price", ""),
        price_details.get("original_cleaners", ""),
        price_details.get("original_hours", ""),
        price_details.get("original_markup_percentage", ""),
        price_details.get("original_markup", "")
    ]
    
    # Check if quote already exists in CSV
    try:
        df = pd.read_csv(csv_path)
        existing_quote = df[df["quote_id"] == quote_data["quote_id"]]
        
        if len(existing_quote) > 0:
            # Update existing quote
            df = df[df["quote_id"] != quote_data["quote_id"]]  # Remove old row
            df.loc[len(df)] = row  # Append new row
            df.to_csv(csv_path, index=False)
        else:
            # Append new quote
            with open(csv_path, "a", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(row)
    except Exception as e:
        print(f"Error saving quote to CSV: {str(e)}")
        # If error (likely CSV doesn't exist yet), create new file
        initialize_csv_if_needed()
        with open(csv_path, "a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(row)
    
    return quote_data["quote_id"]

def get_quotes_dataframe():
    """Read quotes from CSV and return as a pandas DataFrame"""
    # Initialize CSV file if it doesn't exist
    initialize_csv_if_needed()
    
    # Get CSV path
    csv_path = os.path.join("data", "quotes.csv")
    
    try:
        return pd.read_csv(csv_path)
    except Exception as e:
        print(f"Error reading quotes CSV: {str(e)}")
        return pd.DataFrame()

def update_csv_sent_to_customer(quote_id, sent=True):
    """Update the sent_to_customer field in the CSV file"""
    return update_csv_field(quote_id, "sent_to_customer", sent)

def update_csv_field(quote_id, field_name, value):
    """Update any field in the CSV file for a specific quote"""
    # Initialize CSV file if it doesn't exist
    initialize_csv_if_needed()
    
    # Get CSV path
    csv_path = os.path.join("data", "quotes.csv")
    
    try:
        # Read the CSV file
        df = pd.read_csv(csv_path)
        
        # Find the quote by ID
        if quote_id in df["quote_id"].values:
            df.loc[df["quote_id"] == quote_id, field_name] = value
            df.to_csv(csv_path, index=False)
            return True
        else:
            print(f"Quote {quote_id} not found in CSV file")
            return False
    except Exception as e:
        print(f"Error updating {field_name} in CSV: {str(e)}")
        return False