import streamlit as st
import json
import os
import pandas as pd
from utils.pricing import load_pricing_config
from utils.config import load_config, save_config

# Set page title and configure page
st.set_page_config(
    page_title="KMI Services - Admin Settings",
    page_icon="💧",
    layout="wide"
)

# App header with logo
col1, col2 = st.columns([1, 5])
with col1:
    st.image("static/images/logo.jpg", width=100)
with col2:
    st.title("Admin Settings")
    st.markdown("Configure pricing and application settings")

# Admin password protection
if "admin_authenticated" not in st.session_state:
    st.session_state.admin_authenticated = False

if not st.session_state.admin_authenticated:
    with st.form("admin_auth_form"):
        st.subheader("Admin Authentication")
        password = st.text_input("Enter admin password", type="password")
        submit = st.form_submit_button("Login")
        
        if submit:
            import os
            # Get admin password from environment variable, fallback to default only in development
            admin_password = os.environ.get("ADMIN_PASSWORD", "admin123")
            
            if password == admin_password:
                st.session_state.admin_authenticated = True
                st.rerun()
            else:
                st.error("Incorrect password")

else:
    # Show settings tabs
    tab1, tab2, tab3 = st.tabs(["Pricing Configuration", "Application Settings", "Theme Settings"])
    
    with tab1:
        st.header("Pricing Configuration")
        
        # Load current pricing configuration
        pricing_config = load_pricing_config()
        
        # Basic pricing settings
        st.subheader("Basic Pricing")
        col1, col2 = st.columns(2)
        
        with col1:
            hourly_rate = st.number_input(
                "Hourly Rate (£)",
                min_value=10.0,
                max_value=50.0,
                value=float(pricing_config["hourly_rate"]),
                step=0.50
            )
            
        with col2:
            markup_percentage = st.number_input(
                "Markup Percentage (%)",
                min_value=0,
                max_value=100,
                value=int(pricing_config["markup_percentage"]),
                step=5
            )
        
        # Hours required based on property size and service type
        st.subheader("Hours Required")
        
        # Convert nested dictionary to DataFrame for easier editing
        hours_data = []
        for service_type, sizes in pricing_config["property_hours"].items():
            for property_size, hours in sizes.items():
                hours_data.append({
                    "Service Type": service_type,
                    "Property Size": property_size,
                    "Hours": hours
                })
        
        hours_df = pd.DataFrame(hours_data)
        
        # Create a pivot table for editing
        hours_pivot = hours_df.pivot(index="Property Size", columns="Service Type", values="Hours")
        
        # Create editable dataframe
        edited_hours = st.data_editor(
            hours_pivot, 
            use_container_width=True,
            hide_index=False,
            key="hours_editor"
        )
        
        # Cleaners required based on property size and service type
        st.subheader("Cleaners Required")
        
        # Convert nested dictionary to DataFrame for easier editing
        cleaners_data = []
        for service_type, sizes in pricing_config["cleaners_required"].items():
            for property_size, cleaners in sizes.items():
                cleaners_data.append({
                    "Service Type": service_type,
                    "Property Size": property_size,
                    "Cleaners": cleaners
                })
        
        cleaners_df = pd.DataFrame(cleaners_data)
        
        # Create a pivot table for editing
        cleaners_pivot = cleaners_df.pivot(index="Property Size", columns="Service Type", values="Cleaners")
        
        # Create editable dataframe
        edited_cleaners = st.data_editor(
            cleaners_pivot, 
            use_container_width=True,
            hide_index=False,
            key="cleaners_editor"
        )
        
        # Region multipliers
        st.subheader("Region Multipliers")
        
        # Convert dictionary to DataFrame for easier editing
        region_data = [{"Region": region, "Multiplier": multiplier} 
                      for region, multiplier in pricing_config["region_multiplier"].items()]
        
        region_df = pd.DataFrame(region_data)
        
        # Create editable dataframe
        edited_regions = st.data_editor(
            region_df,
            use_container_width=True,
            hide_index=True,
            key="region_editor",
            num_rows="fixed"
        )
        
        # Extra costs
        st.subheader("Additional Service Costs")
        
        # Convert dictionary to DataFrame for easier editing
        extra_costs_data = [{"Service": service, "Cost (£)": cost} 
                           for service, cost in pricing_config["extra_costs"].items()]
        
        extra_costs_df = pd.DataFrame(extra_costs_data)
        
        # Create editable dataframe
        edited_extra_costs = st.data_editor(
            extra_costs_df,
            use_container_width=True,
            hide_index=True,
            key="extra_costs_editor",
            num_rows="fixed"
        )
        
        # Save changes button
        if st.button("Save Pricing Configuration"):
            # Update pricing configuration from edited data
            
            # Update basic pricing
            updated_config = pricing_config.copy()
            updated_config["hourly_rate"] = hourly_rate
            updated_config["markup_percentage"] = markup_percentage
            
            # Update hours required
            updated_hours = {}
            for service_type in pricing_config["property_hours"].keys():
                updated_hours[service_type] = {}
                for property_size in pricing_config["property_hours"][service_type].keys():
                    updated_hours[service_type][property_size] = edited_hours.loc[property_size, service_type]
            
            updated_config["property_hours"] = updated_hours
            
            # Update cleaners required
            updated_cleaners = {}
            for service_type in pricing_config["cleaners_required"].keys():
                updated_cleaners[service_type] = {}
                for property_size in pricing_config["cleaners_required"][service_type].keys():
                    updated_cleaners[service_type][property_size] = int(edited_cleaners.loc[property_size, service_type])
            
            updated_config["cleaners_required"] = updated_cleaners
            
            # Update region multipliers
            updated_regions = {}
            for _, row in edited_regions.iterrows():
                updated_regions[row["Region"]] = row["Multiplier"]
            
            updated_config["region_multiplier"] = updated_regions
            
            # Update extra costs
            updated_extra_costs = {}
            for _, row in edited_extra_costs.iterrows():
                updated_extra_costs[row["Service"]] = row["Cost (£)"]
            
            updated_config["extra_costs"] = updated_extra_costs
            
            # Save updated configuration
            config_dir = os.path.join("config")
            os.makedirs(config_dir, exist_ok=True)
            
            config_path = os.path.join(config_dir, "pricing_config.json")
            with open(config_path, "w") as file:
                json.dump(updated_config, file, indent=4)
                
            st.success("Pricing configuration saved successfully!")
    
    with tab2:
        st.header("Application Settings")
        
        # Load current application configuration
        app_config = load_config()
        
        # Company information
        st.subheader("Company Information")
        
        col1, col2 = st.columns(2)
        
        with col1:
            company_name = st.text_input("Company Name", value=app_config["company_name"])
            company_email = st.text_input("Company Email", value=app_config["company_email"])
            
        with col2:
            company_website = st.text_input("Company Website", value=app_config["company_website"])
        
        # Email settings
        st.subheader("Email Settings")
        
        email_settings = app_config["email_settings"]
        
        col1, col2 = st.columns(2)
        
        with col1:
            smtp_server = st.text_input("SMTP Server", value=email_settings["smtp_server"])
            smtp_port = st.number_input("SMTP Port", value=email_settings["smtp_port"], min_value=1, max_value=65535)
            
        with col2:
            smtp_username = st.text_input("SMTP Username", value=email_settings["smtp_username"])
            smtp_password = st.text_input("SMTP Password", type="password", value=email_settings["smtp_password"])
            from_email = st.text_input("From Email", value=email_settings["from_email"])
        
        # Save settings button
        if st.button("Save Application Settings"):
            # Update application configuration
            updated_config = {
                "company_name": company_name,
                "company_email": company_email,
                "company_website": company_website,
                "email_settings": {
                    "smtp_server": smtp_server,
                    "smtp_port": smtp_port,
                    "smtp_username": smtp_username,
                    "smtp_password": smtp_password,
                    "from_email": from_email
                }
            }
            
            # Save updated configuration
            if save_config(updated_config):
                st.success("Application settings saved successfully!")
            else:
                st.error("Failed to save application settings.")
    
    # Theme settings
    with tab3:
        st.header("Theme Settings")
        st.info("Customise the appearance of the application with these theme settings.")
        
        # Read the current theme settings from config.toml
        import toml
        import os.path
        config_path = os.path.join(".streamlit", "config.toml")
        
        # Initialize config as empty dict as a fallback
        config = {}
        
        if os.path.exists(config_path):
            try:
                config = toml.load(config_path)
                theme = config.get("theme", {})
            except Exception as e:
                st.warning(f"Could not load config file: {e}")
                theme = {}
        else:
            theme = {}
        
        # Set default values if not present
        primary_color = theme.get("primaryColor", "#22C7D6")
        background_color = theme.get("backgroundColor", "#FFFFFF")
        secondary_bg_color = theme.get("secondaryBackgroundColor", "#F0F2F6")
        text_color = theme.get("textColor", "#262730")
        font = theme.get("font", "sans serif")
        
        st.subheader("Colour Settings")
        col1, col2 = st.columns(2)
        
        with col1:
            new_primary_color = st.color_picker("Primary Colour", primary_color)
            new_background_color = st.color_picker("Background Colour", background_color)
        
        with col2:
            new_secondary_bg_color = st.color_picker("Secondary Background Colour", secondary_bg_color)
            new_text_color = st.color_picker("Text Colour", text_color)
        
        st.subheader("Font Settings")
        new_font = st.selectbox(
            "Font Family",
            options=["sans serif", "serif", "monospace"],
            index=["sans serif", "serif", "monospace"].index(font) if font in ["sans serif", "serif", "monospace"] else 0
        )
        
        # Save theme settings
        if st.button("Save Theme Settings"):
            # Create the theme section in the config
            if "theme" not in config:
                config["theme"] = {}
            
            # Update theme settings
            config["theme"]["primaryColor"] = new_primary_color
            config["theme"]["backgroundColor"] = new_background_color
            config["theme"]["secondaryBackgroundColor"] = new_secondary_bg_color
            config["theme"]["textColor"] = new_text_color
            config["theme"]["font"] = new_font
            
            # Save the updated config
            try:
                os.makedirs(".streamlit", exist_ok=True)
                with open(config_path, "w") as f:
                    toml.dump(config, f)
                st.success("Theme settings saved successfully! Please restart the application for changes to take effect.")
            except Exception as e:
                st.error(f"Failed to save theme settings: {str(e)}")
    
    # Logout button
    if st.button("Logout"):
        st.session_state.admin_authenticated = False
        st.rerun()