import streamlit as st
import datetime
import os
import json
import pandas as pd
from utils.pricing import calculate_price
from utils.email_service import send_customer_email, send_business_email
from utils.data_storage import save_quote_to_csv
from utils.database import save_quote_to_db, initialize_db

# Initialize session state variables
if "show_service_details" not in st.session_state:
    st.session_state.show_service_details = False

# Set page title and configure page
st.set_page_config(
    page_title="KMI Services - Cleaning Quote Calculator",
    page_icon="💧",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Initialize session state for form data
if 'form_submitted' not in st.session_state:
    st.session_state.form_submitted = False

if 'quote_data' not in st.session_state:
    st.session_state.quote_data = {}
    
# Initialize carpet cleaning session state
if 'carpet_cleaning' not in st.session_state:
    st.session_state.carpet_cleaning = False
if 'carpet_rooms' not in st.session_state:
    st.session_state.carpet_rooms = 0

# Carpet cleaning is now handled inside the form
    
# Admin mode toggle in sidebar
if 'admin_mode' not in st.session_state:
    st.session_state.admin_mode = False
    
with st.sidebar:
    st.session_state.admin_mode = st.checkbox("Admin Mode (Staff Use Only)", 
                                         value=st.session_state.admin_mode,
                                         help="When enabled, quotes will be sent to the business for review instead of directly to customers")
    
    # We've moved the carpet cleaning controls to after the form

# App header with logo
col1, col2 = st.columns([1, 3])
with col1:
    st.image("static/images/logo.jpg", width=120)
with col2:
    st.title("KMI Services Quote Calculator")
    st.markdown("""
        Get an instant quote for our professional cleaning services. 
        Fill in the form below with your requirements.
    """)

# Create service description tooltips
service_descriptions = {
    "Oven Clean": "Deep cleaning inside the oven, removing grease and burnt-on residue (may require specialist cleaners).",
    "Carpet Cleaning": "Using specialist equipment to deep clean carpets. Base price includes 1 room; additional charges apply for extra rooms (to be discussed with customer).",
    "Internal Windows": "Cleaning of all interior window glass surfaces and frames.",
    "External Windows": "Cleaning outside window glass (requires additional equipment and usually an extra cleaner).",
    "Balcony/Patio": "Sweeping and washing outdoor balcony or patio areas."
}

# Main form
with st.form("quote_form"):
    # Customer Information
    st.subheader("Customer Information")
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Full Name")
        phone = st.text_input("Phone Number")
        email = st.text_input("Email Address")
    with col2:
        address = st.text_input("Address")
        postcode = st.text_input("Postcode")
        
    # Referral information
    referral_source = st.selectbox(
        "How did you find us?", 
        options=["Please select...", "Google", "Facebook", "Word of Mouth", "Family/Friend Recommendation", "Other"]
    )
    
    # Initialize referral_other with empty string
    referral_other = ""
    if referral_source == "Other":
        referral_other = st.text_input("Please specify how you found us")
    
    # Property Information
    st.subheader("Property Information")
    
    col1, col2 = st.columns(2)
    with col1:
        region = st.selectbox(
            "Region", 
            options=["Bedfordshire", "Buckinghamshire", "Hertfordshire", "North London"]
        )
        
        property_size = st.selectbox(
            "Property Size", 
            options=["1 Bedroom", "2 Bedroom", "3 Bedroom", "4 Bedroom", "5+ Bedroom"]
        )
    
    with col2:
        num_bathrooms = st.number_input(
            "Number of Bathrooms", 
            min_value=1, 
            max_value=10, 
            value=1
        )
        
        num_reception_rooms = st.number_input(
            "Number of Reception Rooms", 
            min_value=1, 
            max_value=10, 
            value=1
        )

    # Service Type
    st.subheader("Service Type")
    
    service_type = st.selectbox(
        "Select Service Type", 
        options=["Regular Clean", "One-Off Clean", "Deep Clean"],
        help="Click the 'Service Details' button below the form to see what's included in each service type"
    )
    
    # Calculate minimum date (3 days from today)
    min_date = datetime.date.today() + datetime.timedelta(days=3)
    
    # Configure date format to UK style (DD/MM/YYYY)
    cleaning_date = st.date_input(
        "Preferred Cleaning Date", 
        value=min_date,
        min_value=min_date,
        help="Dates must be at least 3 days in the future to allow time for cleaner scheduling",
        format="DD/MM/YYYY"  # UK date format
    )
    
    # House condition factors
    st.subheader("House Condition")
    col1, col2 = st.columns(2)
    with col1:
        cleanliness_level = st.selectbox(
            "Current Cleanliness Level", 
            options=["Very Clean", "Normal", "Somewhat Dirty", "Very Dirty"],
            help="This helps us estimate the cleaning time required"
        )
    with col2:
        pet_status = st.selectbox(
            "Pets in Home", 
            options=["No Pets", "Small Pet (e.g., cat, small dog)", "Large Pet (e.g., large dog)", "Multiple Pets"],
            help="Pets can affect cleaning time due to pet hair and dander"
        )
    
    # Note about cleaners
    st.info("**Note:** The number of cleaners will be determined based on your property size, service type, and additional options to ensure the job is completed within a reasonable timeframe (maximum 7.5 hour working day).")
    
    # Additional Services
    st.subheader("Additional Services")
    
    # Info text to explain additional services
    st.info("""
    **Note:** The services below are not included in any of the standard cleaning packages and require 
    specialized equipment, cleaning products, or additional time. Adding these will increase the total cost 
    and may require additional cleaners to complete the job within a reasonable timeframe.
    """)
    
    # Service descriptions are defined at the top of the file
    
    # Using carpet cleaning session state initialized at the top of the file
    
    st.write("### Standard Additional Services")
    col1, col2 = st.columns(2)
    with col1:
        oven_clean = st.checkbox("Oven Clean", help=service_descriptions["Oven Clean"])
        # Simplified carpet cleaning checkbox
        carpet_cleaning = st.checkbox(
            "Carpet Cleaning (1 Room)", 
            value=st.session_state.carpet_cleaning,
            key="carpet_cleaning_form",
            help=service_descriptions["Carpet Cleaning"]
        )
        # Update session state
        st.session_state.carpet_cleaning = carpet_cleaning
        
        # Always set to 1 room when selected, 0 when not
        if carpet_cleaning:
            st.session_state.carpet_rooms = 1
        else:
            st.session_state.carpet_rooms = 0
        
    with col2:
        internal_windows = st.checkbox("Internal Windows", help=service_descriptions["Internal Windows"])
        # Hidden for now, but keeping the code for future external cleaning form
        # external_windows = st.checkbox("External Windows", help=service_descriptions["External Windows"])
        external_windows = False  # Setting this to False since we're hiding it
        balcony_patio = st.checkbox("Sweep Balcony/Patio", help=service_descriptions["Balcony/Patio"])
    
    cleaning_materials = st.checkbox("Cleaning Materials Required", 
                                help="Select this if you would like our cleaners to bring all necessary cleaning products and supplies. Additional fee applies.")
    
    # Notes for customers
    st.markdown("""---""")
    st.write("Any additional notes or special requirements for the cleaning team:")
    customer_notes = st.text_area("Customer notes", 
                                placeholder="Example: School run until 9:15am, please arrive after this time. Let yourself in through side gate if not home.",
                                height=100)
    
    # View service details link
    service_details_link = st.form_submit_button("View Service Details", type="secondary")
    
    # Submit button with blue color and white text
    submitted = st.form_submit_button("Calculate Quote", type="primary")
    
    if service_details_link:
        st.session_state.show_service_details = True
        st.rerun()
        
    if submitted:
        # Validate required fields
        if not name or not email or not address or not postcode:
            st.error("Please fill in all required customer information fields.")
        else:
            # Carpet cleaning is already managed by the checkbox outside the form
            # Collect all form data
            # Gather referral information
            if referral_source == "Other":
                referral_data = {
                    "referral_source": referral_source,
                    "referral_other": referral_other
                }
            else:
                referral_data = {
                    "referral_source": referral_source,
                    "referral_other": ""
                }
                
            quote_data = {
                "customer_info": {
                    "name": name,
                    "email": email,
                    "phone": phone,
                    "address": address,
                    "postcode": postcode,
                    "referral_source": referral_data["referral_source"],
                    "referral_other": referral_data["referral_other"]
                },
                "property_info": {
                    "region": region,
                    "property_size": property_size,
                    "num_bathrooms": num_bathrooms,
                    "num_reception_rooms": num_reception_rooms
                },
                "service_info": {
                    "service_type": service_type,
                    "cleaning_date": cleaning_date.strftime("%d/%m/%Y"),  # UK date format DD/MM/YYYY
                    "cleanliness_level": cleanliness_level,
                    "pet_status": pet_status,
                    "cleaner_preference": "No Preference",  # Auto-assign cleaners based on job requirements
                    "customer_notes": customer_notes,
                    "additional_services": {
                        "oven_clean": oven_clean,
                        "carpet_cleaning": st.session_state.carpet_cleaning,
                        "carpet_rooms": st.session_state.carpet_rooms,
                        "internal_windows": internal_windows,
                        "external_windows": external_windows,
                        "balcony_patio": balcony_patio
                    },
                    "cleaning_materials": cleaning_materials
                }
            }
            
            # Calculate price
            price_details = calculate_price(quote_data)
            quote_data["price_details"] = price_details
            
            # Initialize database
            initialize_db()
            
            # Save to session state
            st.session_state.quote_data = quote_data
            st.session_state.form_submitted = True
            st.rerun()

# Carpet cleaning is now handled inside the form

# Display service details when button is clicked
if st.session_state.get("show_service_details", False):
    service_details = {
        "Regular Clean": """
        **Regular cleaning services include:**
        
        ✅ Hoovering and mopping the floors
        ✅ Cleaning bathrooms – sink, mirror, bath and toilet
        ✅ Tidying up
        ✅ Cleaning the kitchen – wiping down work surfaces, cupboard doors, hob
        
        **Not included** (available as additional services):
        - Oven cleaning (inside)
        - Carpet deep cleaning
        - Window cleaning (internal or external)
        - Balcony/patio cleaning
        """,
        
        "One-Off Clean": """
        **One-off cleaning services include everything in Regular Clean plus:**
        
        ✅ Cleaning under furniture
        ✅ Cleaning blinds
        ✅ Vacuum and clean upholstery
        ✅ Dust individual decorations and lamp shades
        ✅ Cleaning skirting boards, window frames, and door frames
        
        **Not included** (available as additional services):
        - Oven cleaning (inside)
        - Carpet deep cleaning
        - Window cleaning (internal or external)
        - Balcony/patio cleaning
        """,
        
        "Deep Clean": """
        **Deep Clean includes everything in One-Off Clean plus:**
        
        ✅ Deep cleaning of kitchen appliances
        ✅ Scale removal from bathrooms
        ✅ Detailed cleaning behind/under furniture
        ✅ Interior window sills and frames
        ✅ Light switches and door handles sanitized
        ✅ Wall marks spot cleaned
        
        **Not included** (available as additional services):
        - Oven cleaning (inside)
        - Carpet deep cleaning
        - External window cleaning
        - Balcony/patio cleaning
        """
    }
    
    st.subheader("Cleaning Service Details")
    for service, details in service_details.items():
        with st.expander(service):
            st.markdown(details)
            
    # Add a button to close the info box
    if st.button("Close", key="close_service_details"):
        st.session_state.show_service_details = False

# Display quote if form was submitted
if st.session_state.form_submitted:
    quote_data = st.session_state.quote_data
    price_details = quote_data["price_details"]
    
    st.header("Your Cleaning Quote")
    
    # Display quote summary
    st.subheader("Quote Summary")
    col1, col2 = st.columns(2)
    
    with col1:
        st.write(f"**Service Type:** {quote_data['service_info']['service_type']}")
        st.write(f"**Property Size:** {quote_data['property_info']['property_size']}")
        st.write(f"**Region:** {quote_data['property_info']['region']}")
        st.write(f"**Date:** {quote_data['service_info']['cleaning_date']}")
        
    with col2:
        st.write(f"**Bathrooms:** {quote_data['property_info']['num_bathrooms']}")
        st.write(f"**Reception Rooms:** {quote_data['property_info']['num_reception_rooms']}")
        st.write(f"**Time Required:** {price_details['hours_required']:.2f} hours")
        st.write(f"**Cleaners Required:** {price_details['cleaners_required']}")
        
        # Add an explanation about the suggested number of cleaners
        additional_services = quote_data['service_info']['additional_services']
        reasons = []
        
        # Check for external windows
        if additional_services.get('external_windows', False):
            reasons.append("external window cleaning")
        
        # Check for oven cleaning
        if additional_services.get('oven_clean', False):
            reasons.append("oven cleaning")
        
        # Check for carpet cleaning
        if additional_services.get('carpet_cleaning', False):
            reasons.append("carpet cleaning (1 room)")
        
        # If there are additional services that affect cleaner count, explain
        if reasons:
            reason_text = ", ".join(reasons[:-1])
            if len(reasons) > 1:
                reason_text += f", and {reasons[-1]}"
            else:
                reason_text = reasons[0]
            
            st.info(f"This job will require {price_details['cleaners_required']} cleaner{'s' if price_details['cleaners_required'] > 1 else ''} to complete within our standard working day (7.5 hours maximum per cleaner). Services like {reason_text} affect the number of cleaners needed.")
            
        if quote_data['service_info']['cleaning_materials']:
            st.write("**Cleaning Materials:** Included")
            
    # Admin adjustments section (only shown if in admin mode)
    if st.session_state.admin_mode:
        st.subheader("Admin Adjustments")
        st.write("Make adjustments to this quote for special circumstances or regular clients.")
        
        adjustment_col1, adjustment_col2 = st.columns(2)
        
        with adjustment_col1:
            # Custom discount for regular bookings
            regular_client = st.checkbox("Regular Client", 
                                        help="Check if client will book regularly")
            if regular_client:
                discount_percentage = st.slider("Regular Client Discount (%)", 
                                              min_value=5, max_value=20, value=10, step=5,
                                              help="Discount percentage for regular clients")
                
                # Calculate discounted price
                original_price = price_details['total_price']
                discount_amount = original_price * (discount_percentage / 100)
                discounted_price = original_price - discount_amount
                
                # Update price details
                price_details['regular_client_discount_percentage'] = discount_percentage
                price_details['regular_client_discount_amount'] = discount_amount
                price_details['original_price'] = original_price
                price_details['total_price'] = discounted_price
                
                st.write(f"Discount Amount: £{discount_amount:.2f}")
                st.write(f"Adjusted Price: £{discounted_price:.2f}")
        
        with adjustment_col2:
            # Adjust number of cleaners
            original_cleaners = price_details['cleaners_required']
            custom_cleaners = st.number_input("Adjust Number of Cleaners", 
                                           min_value=1, max_value=5, 
                                           value=original_cleaners,
                                           help="Override the calculated number of cleaners")
            
            if custom_cleaners != original_cleaners:
                # Adjust hours and recalculate price if needed
                hours_per_cleaner = price_details['hours_required'] / original_cleaners
                new_hours = hours_per_cleaner * custom_cleaners
                
                price_details['original_cleaners'] = original_cleaners
                price_details['cleaners_required'] = custom_cleaners
                price_details['original_hours'] = price_details['hours_required']
                price_details['hours_required'] = new_hours
                
                st.write(f"Adjusted Hours: {new_hours:.2f} hours")
                
            # Override markup percentage
            custom_markup = st.slider("Adjust Markup (%)", 
                                   min_value=0, max_value=40, 
                                   value=int(price_details['markup_percentage']), 
                                   step=5,
                                   help="Override the standard markup percentage")
            
            if custom_markup != price_details['markup_percentage']:
                original_markup_pct = price_details['markup_percentage']
                original_markup = price_details['markup']
                
                # Calculate new markup and total
                new_markup = price_details['subtotal'] * (custom_markup / 100)
                new_total = price_details['subtotal'] + new_markup
                
                # Store original values and update
                price_details['original_markup_percentage'] = original_markup_pct
                price_details['original_markup'] = original_markup
                price_details['markup_percentage'] = custom_markup
                price_details['markup'] = new_markup
                
                # If we also have a regular client discount, apply it after the new markup
                if regular_client:
                    discount_amount = new_total * (discount_percentage / 100)
                    price_details['regular_client_discount_amount'] = discount_amount
                    price_details['total_price'] = new_total - discount_amount
                else:
                    price_details['total_price'] = new_total
                
                st.write(f"Original Markup: {original_markup_pct}% (£{original_markup:.2f})")
                st.write(f"New Markup: {custom_markup}% (£{new_markup:.2f})")
        
        # Notes section for admin
        st.write("### Admin Notes")
        admin_notes = st.text_area("Add notes about price adjustments (internal use only)", 
                                 value="", height=100)
        if admin_notes:
            price_details['admin_notes'] = admin_notes
            
        st.write("### Customer Notes")
        customer_notes = st.text_area("Add notes for the cleaning team (will be visible to customer)",
                                    placeholder="Example: School run until 9:15am, please arrive after this time. Let yourself in through side gate if not home.",
                                    value=quote_data["service_info"].get("customer_notes", ""), 
                                    height=100)
        if customer_notes:
            quote_data["service_info"]["customer_notes"] = customer_notes
            
        # Update the quote data with modified price details
        quote_data["price_details"] = price_details
    
    # House condition information in the KMI team expander
    house_cleanliness = quote_data['service_info'].get('cleanliness_level', 'Normal')
    pet_status = quote_data['service_info'].get('pet_status', 'No Pets')
    
    st.subheader("Additional Services")
    additional = quote_data['service_info']['additional_services']
    if any(additional.values()):
        if additional['oven_clean']:
            st.write("- Oven Clean")
        if additional['carpet_cleaning']:
            st.write("- Carpet Cleaning (1 room) - Additional charges apply for extra rooms")
        if additional['internal_windows']:
            st.write("- Internal Windows")
        if additional['external_windows']:
            st.write("- External Windows")
        if additional['balcony_patio']:
            st.write("- Sweep Balcony/Patio")
    else:
        st.write("None selected")
    
    # Customer view (simplified price)
    st.subheader("Price")
    st.markdown(f"### Total Price: £{price_details['total_price']:.2f}")
    
    # Add an expander for KMI Team members to see full breakdown
    with st.expander("KMI Team - Detailed Price Breakdown"):
        st.markdown("### Detailed Breakdown (For KMI Team Only)")
        
        st.write(f"**House Condition Factors:**")
        st.write(f"- **Cleanliness Level:** {house_cleanliness}")
        st.write(f"- **Pet Status:** {pet_status}")
        
        st.write(f"**Hourly Rate:** £{price_details['hourly_rate']:.2f}")
        # Show hours with 1 decimal place
        st.write(f"**Hours Required:** {price_details['hours_required']:.2f}")
        st.write(f"**Cleaners Required:** {price_details['cleaners_required']}")
        
        # Add explanation about how cleaning time is calculated
        st.write("**Factors affecting cleaner count:**")
        
        # Determine if this is a large property
        property_size = quote_data['property_info']['property_size']
        is_large_property = property_size in ["4 Bedroom", "5+ Bedroom"]
        
        # List factors affecting cleaner count
        total_labor_hours = price_details['hours_required'] * price_details['cleaners_required']
        st.write(f"- *Total job time: {total_labor_hours:.2f} hours*")
        st.write(f"- *Maximum hours per cleaner: 7.5 hours per day*")
        
        if is_large_property:
            st.write(f"- *Large property ({property_size})*")
            
        # List service-specific factors
        if additional['external_windows']:
            st.write("- *External window cleaning requires an additional cleaner*")
        if additional['oven_clean']:
            st.write("- *Oven cleaning affects total cleaning time*")
        if additional['carpet_cleaning']:
            st.write("- *Carpet cleaning (1 room) requires additional time. Extra rooms will incur additional charges.*")
        if additional['oven_clean'] and additional['carpet_cleaning'] and is_large_property:
            st.write("- *Combination of oven cleaning and carpet cleaning in a large property*")
            
        st.write(f"**Region Multiplier:** {price_details['region_multiplier']:.2f}")
        
        st.write(f"**Base Price:** £{price_details['base_price']:.2f}")
        
        if price_details['extra_bathrooms_cost'] > 0:
            st.write(f"**Extra Bathrooms:** £{price_details['extra_bathrooms_cost']:.2f}")
        
        if price_details['extra_reception_cost'] > 0:
            st.write(f"**Extra Reception Rooms:** £{price_details['extra_reception_cost']:.2f}")
        
        # Additional services costs
        if additional['oven_clean']:
            st.write(f"**Oven Clean:** £{price_details['extra_costs']['oven_clean']:.2f}")
            
        if additional['carpet_cleaning']:
            carpet_cost = price_details['extra_costs']['carpet_cleaning_per_room'] * additional['carpet_rooms']
            st.write(f"**Carpet Cleaning:** £{carpet_cost:.2f}")
            
        if additional['internal_windows']:
            st.write(f"**Internal Windows:** £{price_details['extra_costs']['internal_windows']:.2f}")
            
        if additional['external_windows']:
            st.write(f"**External Windows:** £{price_details['extra_costs']['external_windows']:.2f}")
            
        if additional['balcony_patio']:
            st.write(f"**Balcony/Patio:** £{price_details['extra_costs']['balcony_patio']:.2f}")
        
        if price_details['materials_cost'] > 0:
            st.write(f"**Cleaning Materials:** £{price_details['materials_cost']:.2f}")
        
        st.write(f"**Subtotal:** £{price_details['subtotal']:.2f}")
        st.write(f"**Markup ({price_details['markup_percentage']}%):** £{price_details['markup']:.2f}")
        st.write(f"**Total Price:** £{price_details['total_price']:.2f}")
    
    # Email quote options
    st.subheader("Next Steps")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Different button text and behavior based on admin mode
        button_text = "Send Quote for Review" if st.session_state.admin_mode else "Request Quote"
        if st.button(button_text, use_container_width=True, type="primary"):
            try:
                # For database tracking - determine if admin created this quote
                quote_data["admin_created"] = st.session_state.admin_mode
                
                # Always mark as not sent to customer initially
                quote_data["sent_to_customer"] = False
                
                # Set initial status to "Enquiry" for new quotes
                quote_data["status"] = "Enquiry"
                
                # Generate the quote ID and save to both CSV and database first
                # This ensures we have a quote ID before sending emails
                quote_id = save_quote_to_csv(quote_data)
                save_quote_to_db(quote_data)
                
                # Make sure we're using the quote_data with the updated quote_id
                quote_data["quote_id"] = quote_id
                
                # If in admin mode, only send to business email (for review by senior staff)
                if st.session_state.admin_mode:
                    send_business_email(quote_data)
                    st.success("Quote sent to the business email for review. It will be sent to the customer after admin approval.")
                else:
                    # Customer mode - only send to business for admin review first
                    send_business_email(quote_data)
                    
                    # Send a courtesy email to customer (without changing sent_to_customer status)
                    # Using direct email sending to avoid changing sent_to_customer flag
                    from utils.email_service import send_email
                    from utils.config import load_config
                    
                    config = load_config()
                    company_name = config["company_name"]
                    customer_email = quote_data['customer_info']['email']
                    customer_name = quote_data['customer_info']['name']
                    quote_id = quote_data.get('quote_id', 'pending')
                    
                    subject = f"Your {company_name} Quote Request Received"
                    
                    # Extract quote details for confirmation
                    property_size = quote_data['property_info']['property_size']
                    service_type = quote_data['service_info']['service_type']
                    cleaning_date = quote_data['service_info']['cleaning_date']
                    
                    # Get cleaner count
                    cleaners_required = price_details.get('cleaners_required', 1)
                    cleaner_text = f"<p><strong>Cleaners Required:</strong> {cleaners_required}</p>"
                    
                    # Get cleanliness level and pet status
                    cleanliness = quote_data['service_info'].get('cleanliness_level', 'Normal')
                    pets = quote_data['service_info'].get('pet_status', 'No Pets')
                    
                    # Build list of additional services
                    additional_services = []
                    if quote_data['service_info']['additional_services']['oven_clean']:
                        additional_services.append("Oven Clean")
                    if quote_data['service_info']['additional_services']['carpet_cleaning']:
                        additional_services.append("Carpet Cleaning (1 room) - Additional charges apply for extra rooms")
                    if quote_data['service_info']['additional_services']['internal_windows']:
                        additional_services.append("Internal Windows")
                    if quote_data['service_info']['additional_services']['external_windows']:
                        additional_services.append("External Windows")
                    if quote_data['service_info']['additional_services']['balcony_patio']:
                        additional_services.append("Balcony/Patio Clean")
                    if quote_data['service_info']['cleaning_materials']:
                        additional_services.append("Cleaning Materials Included")
                    
                    # Create additional services HTML
                    additional_services_html = ""
                    if additional_services:
                        additional_services_html = "<p><strong>Additional Services:</strong></p><ul>"
                        for service in additional_services:
                            additional_services_html += f"<li>{service}</li>"
                        additional_services_html += "</ul>"
                    
                    html_content = f"""
                    <html>
                    <head>
                        <style>
                            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                            h1 {{ color: #22C7D6; }}
                            h2 {{ color: #22C7D6; }}
                            .content {{ background-color: #f9f9f9; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
                            .footer {{ margin-top: 30px; font-size: 12px; color: #777; text-align: center; }}
                        </style>
                    </head>
                    <body>
                        <div class="container">
                            <h1>Thank You For Your Quote Request</h1>
                            
                            <div class="content">
                                <p>Dear {customer_name},</p>
                                
                                <p>Thank you for requesting a quote from {company_name}. We have received your request and our team is reviewing your details.</p>
                                
                                <p><strong>Your reference number:</strong> {quote_id}</p>
                                
                                <h2>Your Request Details</h2>
                                <p><strong>Property Size:</strong> {property_size}</p>
                                <p><strong>Service Type:</strong> {service_type}</p>
                                <p><strong>Preferred Date:</strong> {cleaning_date}</p>
                                <p><strong>Cleanliness Level:</strong> {cleanliness}</p>
                                <p><strong>Pets:</strong> {pets}</p>
                                {cleaner_text}
                                {additional_services_html}
                                
                                <p>We'll be in touch shortly with your customised quote and pricing details. Once you receive it, you'll be able to:</p>
                                
                                <ul>
                                    <li>Review your complete quote details with pricing</li>
                                    <li>Accept the quote (if it meets your needs)</li>
                                    <li>Request your preferred cleaning date and time</li>
                                </ul>
                                
                                <p>If you have any questions in the meantime, please feel free to contact us by replying to this email.</p>
                            </div>
                            
                            <p>Thank you for considering {company_name}!</p>
                            <p>Best regards,<br>The {company_name} Team</p>
                            
                            <div class="footer">
                                <p>{company_name} | www.kmiservices.co.uk</p>
                            </div>
                        </div>
                    </body>
                    </html>
                    """
                    
                    # Send courtesy email to customer
                    send_email(customer_email, subject, html_content)
                    
                    st.success(f"""
                    Thank you for your quote request!
                    
                    Our team will review your requirements and send you a customised quote shortly.
                    We'll contact you at {customer_email} with your quote details.
                    
                    Your reference number: {quote_id}
                    
                    We've sent a confirmation email to your address with these details.
                    """)
            except Exception as e:
                st.error(f"Failed to send email: {str(e)}")
    
    with col2:
        if st.button("Request Cleaning Schedule", use_container_width=True, type="primary"):
            # Create a form for scheduling details
            with st.form("scheduling_form"):
                st.subheader("Request Cleaning Schedule")
                st.write("Please tell us your preferred date and time. Our team will confirm availability with our cleaning staff and contact you to finalize your booking.")
                
                # Confirm date - minimum 3 days in the future
                min_date = datetime.date.today() + datetime.timedelta(days=3)
                
                # Get the date from the quote data - check if it's in UK or ISO format
                try:
                    if "/" in quote_data["service_info"]["cleaning_date"]:
                        # Parse UK format DD/MM/YYYY
                        quote_date = datetime.datetime.strptime(quote_data["service_info"]["cleaning_date"], "%d/%m/%Y").date()
                    else:
                        # Parse ISO format YYYY-MM-DD
                        quote_date = datetime.datetime.strptime(quote_data["service_info"]["cleaning_date"], "%Y-%m-%d").date()
                except ValueError:
                    # Fallback to today if parsing fails
                    quote_date = datetime.date.today()
                
                # Use the later of the two dates (quote date or min_date) as the default value
                default_date = max(quote_date, min_date)
                
                schedule_date = st.date_input(
                    "Confirm Cleaning Date", 
                    value=default_date,
                    min_value=min_date,
                    help="Dates must be at least 3 days in the future to allow time for cleaner scheduling",
                    format="DD/MM/YYYY"  # UK date format
                )
                
                # Add time preference based on cleaning duration
                cleaning_hours = quote_data["price_details"]["hours_required"]
                if cleaning_hours > 3:
                    st.info("Due to the estimated cleaning time of {:.1f} hours, this cleaning can only be scheduled in the morning.".format(cleaning_hours))
                    time_preference = "Morning (8am-12pm)"
                    st.write(f"**Time Preference:** {time_preference}")
                else:
                    time_preference = st.radio(
                        "Preferred Time", 
                        options=["Morning (8am-12pm)", "Afternoon (12pm-5pm)"]
                    )
                    
                # Customer notes field for important information
                customer_notes = st.text_area(
                    "Notes for Cleaners",
                    placeholder="Example: School run until 9:15am, please arrive after this time. Let yourself in through side gate if not home.",
                    help="Add any important information for the cleaning team, such as access details, specific requirements, or preferred arrival times."
                )
                
                # Submit button
                submit_schedule = st.form_submit_button("Submit Cleaning Request")
                
                if submit_schedule:
                    try:
                        # Update status to "Schedule Requested" (not fully scheduled yet)
                        quote_data["status"] = "Schedule Requested"
                        quote_data["service_info"]["cleaning_date"] = schedule_date.strftime("%Y-%m-%d")
                        quote_data["service_info"]["time_preference"] = time_preference
                        quote_data["service_info"]["customer_notes"] = customer_notes
                        
                        # Always mark as not sent to customer until admin approves
                        quote_data["sent_to_customer"] = False
                        quote_data["admin_created"] = False
                        
                        # Save to both CSV and database first to ensure we have a quote_id
                        quote_id = save_quote_to_csv(quote_data)
                        save_quote_to_db(quote_data)
                        
                        # Make sure we're using the quote_data with the updated quote_id
                        quote_data["quote_id"] = quote_id
                        
                        # Send acknowledgment email to customer
                        # Create a simplified version of the customer email for acknowledgment
                        customer_email = quote_data["customer_info"]["email"]
                        customer_name = quote_data["customer_info"]["name"]
                        
                        # Send business email for review
                        send_business_email(quote_data, is_scheduled=True)
                        
                        # Send a courtesy email to customer (without changing sent_to_customer status)
                        # Using direct email sending to avoid changing sent_to_customer flag
                        from utils.email_service import send_email
                        from utils.config import load_config
                        
                        config = load_config()
                        company_name = config["company_name"]
                        
                        subject = f"Your {company_name} Cleaning Date Request"
                        html_content = f"""
                        <html>
                        <head>
                            <style>
                                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                                h1 {{ color: #22C7D6; }}
                                h2 {{ color: #22C7D6; }}
                                .content {{ background-color: #f9f9f9; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
                                .footer {{ margin-top: 30px; font-size: 12px; color: #777; text-align: center; }}
                            </style>
                        </head>
                        <body>
                            <div class="container">
                                <h1>Thank You For Your Cleaning Date Request</h1>
                                
                                <div class="content">
                                    <p>Dear {customer_name},</p>
                                    
                                    <p>Thank you for accepting our quote and requesting a cleaning date. We have received your preferred date and time:</p>
                                    
                                    <p><strong>Date:</strong> {schedule_date.strftime('%d %B %Y')}<br>
                                    <strong>Time:</strong> {time_preference}</p>
                                    
                                    <p>Our team will check contractor availability and contact you shortly to confirm your booking.</p>
                                    
                                    <p>By proceeding with this booking, you agree to our <a href="https://kmiservices.co.uk/terms">Terms and Conditions</a>.</p>
                                    
                                    <p>If you have any questions or need to make changes to your request, please reply to this email or call us directly.</p>
                                </div>
                                
                                <p>Thank you for choosing {company_name}!</p>
                                <p>Best regards,<br>The {company_name} Team</p>
                                
                                <div class="footer">
                                    <p>{company_name} | www.kmiservices.co.uk</p>
                                </div>
                            </div>
                        </body>
                        </html>
                        """
                        
                        # Send courtesy email to customer
                        send_email(customer_email, subject, html_content)
                        
                        st.success(f"""
                        Thank you for accepting our quote and requesting a cleaning date!
                        
                        We have received your preferred cleaning date ({schedule_date.strftime('%d %B %Y')}, {time_preference}).
                        
                        Our team will check contractor availability and contact you to confirm your booking.
                        
                        We've sent a confirmation email to {customer_email} with your booking request details.
                        
                        By proceeding with this booking, you agree to our Terms and Conditions.
                        """)
                    except Exception as e:
                        st.error(f"Failed to schedule cleaning: {str(e)}")
    
    # Reset form option
    if st.button("Create New Quote", use_container_width=True, type="primary"):
        st.session_state.form_submitted = False
        st.session_state.quote_data = {}
        st.rerun()
