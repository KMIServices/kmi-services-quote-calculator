import os
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def load_config():
    """Load application configuration"""
    config_path = os.path.join("config", "app_config.json")
    
    # If config file doesn't exist, create it with default values
    if not os.path.exists(config_path):
        default_config = get_default_config()
        save_config(default_config)
        return default_config
    
    # Load config from file
    try:
        with open(config_path, "r") as file:
            return json.load(file)
    except Exception as e:
        print(f"Error loading config: {str(e)}")
        return get_default_config()

def get_default_config():
    """Return default application configuration"""
    return {
        "company_name": "KMI Services",
        "company_email": "info@kmiservices.co.uk",
        "company_website": "www.kmiservices.co.uk",
        "email_settings": {
            "smtp_server": "smtp.example.com",
            "smtp_port": 587,
            "smtp_username": "",
            "smtp_password": "",
            "from_email": "info@kmiservices.co.uk"
        }
    }

def save_config(config):
    """Save application configuration to JSON file"""
    # Create config directory if it doesn't exist
    config_dir = os.path.join("config")
    os.makedirs(config_dir, exist_ok=True)
    
    # Save config to file
    try:
        config_path = os.path.join(config_dir, "app_config.json")
        with open(config_path, "w") as file:
            json.dump(config, file, indent=4)
        return True
    except Exception as e:
        print(f"Error saving config: {str(e)}")
        return False