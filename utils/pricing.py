import os
import json
import math

def load_pricing_config():
    """Load pricing configuration from JSON file"""
    config_path = os.path.join("config", "pricing_config.json")
    
    # If config file doesn't exist, create it with default values
    if not os.path.exists(config_path):
        default_config = get_default_pricing_config()
        
        # Create config directory if it doesn't exist
        config_dir = os.path.join("config")
        os.makedirs(config_dir, exist_ok=True)
        
        # Save default config to file
        with open(config_path, "w") as file:
            json.dump(default_config, file, indent=4)
        
        return default_config
    
    # Load config from file
    try:
        with open(config_path, "r") as file:
            return json.load(file)
    except Exception as e:
        print(f"Error loading pricing config: {str(e)}")
        return get_default_pricing_config()

def get_default_pricing_config():
    """Return default pricing configuration"""
    return {
        "hourly_rate": 20.0,
        "markup_percentage": 30,
        # Base times in hours for one cleaner (weekly standard clean)
        # Based on professional cleaning service estimates
        "property_hours": {
            "Regular Clean": {
                "1 Bedroom": 2.5,  # ~2.5 hours with 1 cleaner (1 bath)
                "2 Bedroom": 3.5,  # ~3.5 hours with 1 cleaner (2 bath)
                "3 Bedroom": 4.0,  # ~4 hours with 1 cleaner (1-2 bath)
                "4 Bedroom": 5.0,  # ~5 hours with 1 cleaner (2-3 bath)
                "5+ Bedroom": 6.0   # ~6 hours with 1 cleaner (3+ bath)
            },
            "One-Off Clean": {
                "1 Bedroom": 3.0,   # Regular + 20% additional time
                "2 Bedroom": 4.2,   # Regular + 20% additional time
                "3 Bedroom": 4.8,   # Regular + 20% additional time
                "4 Bedroom": 6.0,   # Regular + 20% additional time
                "5+ Bedroom": 7.2    # Regular + 20% additional time
            },
            "Deep Clean": {
                "1 Bedroom": 3.75,  # Regular + 50% additional time
                "2 Bedroom": 5.25,  # Regular + 50% additional time
                "3 Bedroom": 6.0,   # Regular + 50% additional time
                "4 Bedroom": 7.5,   # Regular + 50% additional time
                "5+ Bedroom": 9.0    # Regular + 50% additional time
            }
        },
        # Default number of cleaners based on property size and service type
        # Optimized for a 7.5 hour maximum working day
        "cleaners_required": {
            "Regular Clean": {
                "1 Bedroom": 1,
                "2 Bedroom": 1,
                "3 Bedroom": 1,
                "4 Bedroom": 1,
                "5+ Bedroom": 1
            },
            "One-Off Clean": {
                "1 Bedroom": 1,
                "2 Bedroom": 1,
                "3 Bedroom": 1,
                "4 Bedroom": 1,
                "5+ Bedroom": 1
            },
            "Deep Clean": {
                "1 Bedroom": 1,
                "2 Bedroom": 1,
                "3 Bedroom": 1,
                "4 Bedroom": 2,
                "5+ Bedroom": 2
            }
        },
        "region_multiplier": {
            "Bedfordshire": 1.0,
            "Buckinghamshire": 1.1,
            "Hertfordshire": 1.15,
            "North London": 1.25
        },
        "extra_costs": {
            "extra_bathroom": 15.0,
            "extra_reception_room": 10.0,
            "oven_clean": 30.0,
            "carpet_cleaning_per_room": 25.0,
            "internal_windows": 20.0,
            "external_windows": 30.0,
            "balcony_patio": 20.0,
            "cleaning_materials": 15.0
        },
        "cleanliness_multiplier": {
            "Very Clean": 0.9,
            "Normal": 1.0,
            "Somewhat Dirty": 1.2,
            "Very Dirty": 1.5
        },
        "pet_multiplier": {
            "No Pets": 1.0,
            "Small Pet (e.g., cat, small dog)": 1.1,
            "Large Pet (e.g., large dog)": 1.2,
            "Multiple Pets": 1.3
        }
    }

def calculate_price(quote_data):
    """Calculate the total price based on the quote data"""
    # Load pricing configuration
    pricing_config = load_pricing_config()
    
    # Extract data from quote
    property_info = quote_data["property_info"]
    service_info = quote_data["service_info"]
    additional_services = service_info["additional_services"]
    
    # Get property size and service type
    property_size = property_info["property_size"]
    service_type = service_info["service_type"]
    region = property_info["region"]
    
    # Basic calculations
    hourly_rate = pricing_config["hourly_rate"]
    hours_required = pricing_config["property_hours"][service_type][property_size]
    
    # Apply cleanliness multiplier if specified
    cleanliness_level = service_info.get("cleanliness_level", "Normal")
    cleanliness_multiplier = pricing_config["cleanliness_multiplier"].get(cleanliness_level, 1.0)
    
    # Apply pet multiplier if specified
    pet_status = service_info.get("pet_status", "No Pets")
    pet_multiplier = pricing_config["pet_multiplier"].get(pet_status, 1.0)
    
    # Adjust hours based on cleanliness and pets
    adjusted_hours = hours_required * cleanliness_multiplier * pet_multiplier
    hours_required = adjusted_hours
    
    # Get default calculated cleaners required
    default_cleaners = pricing_config["cleaners_required"][service_type][property_size]
    
    # Apply customer's cleaner preference if specified
    cleaner_preference = service_info.get("cleaner_preference", "No Preference")
    
    # Total labor hours is the product of default cleaners and default hours
    total_labor_hours = hours_required * default_cleaners
    
    # Maximum hours per working day (standard work day with breaks)
    MAX_WORK_DAY_HOURS = 7.5
    
    # Base calculation of required cleaners to fit within a working day
    base_recommended_cleaners = math.ceil(total_labor_hours / MAX_WORK_DAY_HOURS)
    
    # Additional cleaner requirements based on property size, service type and additional services
    is_small_property = property_size in ["1 Bedroom", "2 Bedroom"]
    is_medium_property = property_size in ["3 Bedroom"]
    is_large_property = property_size in ["4 Bedroom", "5+ Bedroom"]
    
    has_oven_clean = additional_services.get("oven_clean", False)
    has_carpet_clean = additional_services.get("carpet_cleaning", False)
    has_external_windows = additional_services.get("external_windows", False)
    has_internal_windows = additional_services.get("internal_windows", False)
    
    is_regular_clean = service_type == "Regular Clean"
    is_one_off_clean = service_type == "One-Off Clean" 
    is_deep_clean = service_type == "Deep Clean"
    
    # Start with base recommended cleaners from hours calculation
    recommended_cleaners = base_recommended_cleaners
    
    # Apply service-specific cleaner requirements based on professional cleaning standards
    # With a MAX_WORK_DAY_HOURS of 7.5 hours per cleaner
    
    # Default base logic: If job takes more than 7.5 hours for one cleaner, add more cleaners
    # This follows the research showing two cleaners can halve the total time on-site
    
    # Use cleaner allocation table from professional cleaning services:
    # Based on input data showing standard cleaning times and cleaner requirements
    
    property_size_mapping = {
        "1 Bedroom": "small",
        "2 Bedroom": "small",
        "3 Bedroom": "medium",
        "4 Bedroom": "large",
        "5+ Bedroom": "large"
    }
    
    property_category = property_size_mapping.get(property_size, "medium")
    
    # 1. External windows always need an extra cleaner regardless of property size
    if has_external_windows:
        recommended_cleaners += 1
    
    # 2. For oven cleaning with other services, add an extra cleaner
    if has_oven_clean and (has_carpet_clean or has_external_windows):
        recommended_cleaners = max(recommended_cleaners, 2)
    
    # 3. Deep cleans for large properties always need at least 2 cleaners
    if is_deep_clean and property_category == "large":
        recommended_cleaners = max(recommended_cleaners, 2)
    
    # 4. Complex jobs with multiple additional services for larger properties need more cleaners
    if property_category == "large" and sum([has_oven_clean, has_carpet_clean, has_external_windows, has_internal_windows]) >= 2:
        recommended_cleaners = max(recommended_cleaners, 2)
        
    # 5. Very high labor hour jobs need additional cleaners to fit within a working day
    # Based on 7.5 hour maximum day:
    if total_labor_hours > 15:  # More than 2 full days for one person
        recommended_cleaners = max(recommended_cleaners, 3)
    elif total_labor_hours > 7.5:  # More than 1 full day for one person
        recommended_cleaners = max(recommended_cleaners, 2)
    
    # Use the system-recommended number of cleaners
    # We've removed the cleaner preference option as requested
    cleaners_required = recommended_cleaners
    
    # Adjust hours to maintain total labor hours
    # When multiple cleaners are assigned, divide the total hours among them
    hours_required = total_labor_hours / cleaners_required
    
    # Ensure total hours per cleaner doesn't exceed max workday
    if hours_required > MAX_WORK_DAY_HOURS:
        # If it still exceeds max hours, add more cleaners until it fits
        while hours_required > MAX_WORK_DAY_HOURS:
            cleaners_required += 1
            hours_required = total_labor_hours / cleaners_required
    
    region_multiplier = pricing_config["region_multiplier"][region]
    
    # Calculate base price
    base_price = hourly_rate * hours_required * cleaners_required * region_multiplier
    
    # Extra costs for additional bathrooms (if more than 1)
    extra_bathrooms = property_info["num_bathrooms"] - 1
    extra_bathrooms_cost = 0
    if extra_bathrooms > 0:
        extra_bathrooms_cost = extra_bathrooms * pricing_config["extra_costs"]["extra_bathroom"]
    
    # Extra costs for additional reception rooms (if more than 1)
    extra_reception_rooms = property_info["num_reception_rooms"] - 1
    extra_reception_cost = 0
    if extra_reception_rooms > 0:
        extra_reception_cost = extra_reception_rooms * pricing_config["extra_costs"]["extra_reception_room"]
    
    # Costs for additional services
    additional_services_cost = 0
    
    if additional_services["oven_clean"]:
        additional_services_cost += pricing_config["extra_costs"]["oven_clean"]
    
    if additional_services["carpet_cleaning"]:
        additional_services_cost += pricing_config["extra_costs"]["carpet_cleaning_per_room"] * additional_services["carpet_rooms"]
    
    if additional_services["internal_windows"]:
        additional_services_cost += pricing_config["extra_costs"]["internal_windows"]
    
    if additional_services["external_windows"]:
        additional_services_cost += pricing_config["extra_costs"]["external_windows"]
    
    if additional_services["balcony_patio"]:
        additional_services_cost += pricing_config["extra_costs"]["balcony_patio"]
    
    # Costs for cleaning materials
    materials_cost = 0
    if service_info["cleaning_materials"]:
        materials_cost = pricing_config["extra_costs"]["cleaning_materials"]
    
    # Calculate subtotal
    subtotal = base_price + extra_bathrooms_cost + extra_reception_cost + additional_services_cost + materials_cost
    
    # Apply markup
    markup_percentage = pricing_config["markup_percentage"]
    markup = subtotal * (markup_percentage / 100)
    total_price = subtotal + markup
    
    # Return price details
    return {
        "hourly_rate": hourly_rate,
        "hours_required": hours_required,
        "cleaners_required": cleaners_required,
        "region_multiplier": region_multiplier,
        "base_price": base_price,
        "extra_bathrooms_cost": extra_bathrooms_cost,
        "extra_reception_cost": extra_reception_cost,
        "additional_services_cost": additional_services_cost,
        "materials_cost": materials_cost,
        "subtotal": subtotal,
        "markup_percentage": markup_percentage,
        "markup": markup,
        "total_price": total_price,
        "extra_costs": pricing_config["extra_costs"]
    }