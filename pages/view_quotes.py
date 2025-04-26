import streamlit as st
import pandas as pd
import io
import os
import uuid
import base64
from datetime import datetime
from utils.database import get_quotes_from_db, update_quote_status, get_quote_by_id, get_db_connection, Quote, update, update_sent_to_customer
from utils.email_service import send_customer_email, send_business_email
from utils.excel_export import create_excel_download_button, download_dataframe_as_excel

# Set page title and configure page
st.set_page_config(
    page_title="KMI Services - View Quotes",
    page_icon="💧",
    layout="wide"
)

# App header with logo
col1, col2 = st.columns([1, 5])
with col1:
    st.image("static/images/logo.jpg", width=100)
with col2:
    st.title("Quotes Database")
    st.markdown("View and manage all quotes in the database")

# Get quotes from database
try:
    quotes_df = get_quotes_from_db()
    
    if len(quotes_df) == 0:
        st.info("No quotes found in the database.")
    else:
        # Add filters
        st.subheader("Filters")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            status_filter = st.multiselect(
                "Status", 
                options=["All"] + sorted(quotes_df["status"].unique().tolist()),
                default="All"
            )
            
        with col2:
            service_filter = st.multiselect(
                "Service Type", 
                options=["All"] + sorted(quotes_df["service_type"].unique().tolist()),
                default="All"
            )
            
        with col3:
            region_filter = st.multiselect(
                "Region", 
                options=["All"] + sorted(quotes_df["region"].unique().tolist()),
                default="All"
            )
        
        # Apply filters
        filtered_df = quotes_df.copy()
        
        if status_filter and "All" not in status_filter:
            filtered_df = filtered_df[filtered_df["status"].isin(status_filter)]
            
        if service_filter and "All" not in service_filter:
            filtered_df = filtered_df[filtered_df["service_type"].isin(service_filter)]
            
        if region_filter and "All" not in region_filter:
            filtered_df = filtered_df[filtered_df["region"].isin(region_filter)]
        
        # Display quotes table
        st.subheader("Quotes")
        
        # Make a copy to modify for display purposes
        display_df = filtered_df.copy()
        
        # Convert boolean admin_created to a more readable indicator
        display_df["source"] = display_df["admin_created"].apply(
            lambda x: "Admin" if x else "Customer"
        )
        
        # Convert boolean columns to more readable Yes/No
        for col in ["oven_clean", "carpet_cleaning", "internal_windows", "external_windows", 
                    "balcony_patio", "cleaning_materials", "sent_to_customer"]:
            display_df[col] = display_df[col].apply(lambda x: "Yes" if x else "No")
        
        # Format price and hour columns
        display_df["total_price"] = display_df["total_price"].apply(lambda x: f"£{x:.2f}")
        display_df["hours_required"] = display_df["hours_required"].apply(lambda x: f"{x:.2f}")
        
        # Split timestamp into date and time columns
        # First convert to datetime if it's not already
        display_df["timestamp"] = pd.to_datetime(display_df["timestamp"])
        # Create separate date and time columns
        display_df["date"] = display_df["timestamp"].dt.strftime("%d/%m/%Y")
        display_df["time"] = display_df["timestamp"].dt.strftime("%H:%M")
        
        # Select all columns to display in the main table, removing "time_preference"
        display_columns = [
            # Quote info
            "quote_id", "date", "time", "status", "source", "sent_to_customer",
            
            # Customer info
            "customer_name", "customer_email", "customer_phone", "customer_address", "customer_postcode",
            "referral_source", "referral_other",
            
            # Property info
            "property_size", "region", "num_bathrooms", "num_reception_rooms",
            
            # Service info
            "service_type", "cleaning_date", "cleanliness_level", "pet_status", "cleaner_preference", 
            "customer_notes",
            
            # Additional services
            "oven_clean", "carpet_cleaning", "carpet_rooms", "internal_windows", 
            "external_windows", "balcony_patio", "cleaning_materials",
            
            # Price details
            "hours_required", "cleaners_required", "total_price",
            
            # Admin details
            "admin_notes"
        ]
        
        # Show the display dataframe with our formatted columns and frozen headers
        st.dataframe(
            display_df[display_columns], 
            use_container_width=True,
            height=400,  # Fixed height to enable vertical scrolling
            column_config={col: st.column_config.Column(col) for col in display_columns}  # Ensure column headers are visible
        )
        
        # Add Excel download button
        excel_file = io.BytesIO()
        with pd.ExcelWriter(excel_file, engine="xlsxwriter") as writer:
            # Create full export with all columns
            display_df.to_excel(writer, sheet_name="All Quotes", index=False)
            # Add formatting
            workbook = writer.book
            worksheet = writer.sheets["All Quotes"]
            # Add header format
            header_format = workbook.add_format({'bold': True, 'bg_color': '#22C7D6', 'color': 'white'})
            for col_num, value in enumerate(display_df.columns.values):
                worksheet.write(0, col_num, value, header_format)
            # Auto-adjust columns' width
            for i, col in enumerate(display_df.columns):
                # Find the maximum length of any entry in this column
                max_len = max(display_df[col].astype(str).apply(len).max(), len(str(col)) + 2)
                worksheet.set_column(i, i, max_len)
        
        excel_file.seek(0)
        
        # Excel export section
        st.markdown("### Export Quote Data")
        
        # Generate timestamp for unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create a simpler CSV approach that's more reliable
        csv_data = display_df.to_csv(index=False).encode('utf-8')
        
        # Use Streamlit's download button with CSV data
        st.download_button(
            label="📥 Download CSV Report",
            data=csv_data,
            file_name="KMI_Quote_Dashboard.csv",
            mime="text/csv"
        )
        
        st.info("""
        **CSV Download Instructions:**
        1. Click the 'Download CSV Report' button above to download the quote data
        2. The CSV file can be opened in Excel, Google Sheets, or any spreadsheet program
        3. For more detailed analysis, you can use the text export below to copy and paste into Excel
        """)
        
        # Alternative CSV approach
        st.markdown("#### Alternative: Copy-Paste CSV Data")
        
        # Create CSV data
        csv_string = display_df.to_csv(index=False)
        
        # Display CSV in a text area
        st.text_area(
            "Or select this text (Ctrl+A), then copy (Ctrl+C) to paste into Excel:",
            csv_string,
            height=200
        )
        
        # Add a clear separator
        st.markdown("---")
        
        # Quote details section
        st.subheader("Quote Details")
        
        # Improved quote selection with search and newest first ordering
        quote_options = filtered_df.sort_values("timestamp", ascending=False)["quote_id"].tolist()
        
        # Add a text input for searching quotes by ID
        search_query = st.text_input("Search quote ID:", placeholder="Type to filter quotes")
        
        # Filter the options based on search query
        if search_query:
            filtered_options = [qid for qid in quote_options if search_query.lower() in qid.lower()]
        else:
            filtered_options = quote_options
            
        # Display top 5 most recent quotes as radio buttons for easy access
        st.write("Quick select recent quotes:")
        recent_quotes = quote_options[:5]  # Get the 5 most recent quotes
        quick_select = st.radio(
            "Recent quotes:",
            options=recent_quotes,
            label_visibility="collapsed",
            horizontal=True
        )
        
        # Select a quote to view details with search-based filtering
        selected_quote_id = st.selectbox(
            "Or select from all quotes:",
            options=filtered_options,
            index=0 if quick_select in filtered_options else 0
        )
        
        # Update selected quote if using quick select
        if quick_select and quick_select != selected_quote_id:
            selected_quote_id = quick_select
        
        if selected_quote_id:
            # Get the selected quote
            selected_quote = filtered_df[filtered_df["quote_id"] == selected_quote_id].iloc[0]
            
            # Display quote details
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("### Customer Information")
                st.write(f"**Name:** {selected_quote['customer_name']}")
                st.write(f"**Email:** {selected_quote['customer_email']}")
                st.write(f"**Address:** {selected_quote['customer_address']}")
                st.write(f"**Postcode:** {selected_quote['customer_postcode']}")
                
                # Show referral information if available
                if 'referral_source' in selected_quote and selected_quote['referral_source']:
                    if selected_quote['referral_source'] == "Other" and selected_quote['referral_other']:
                        st.write(f"**Referral Source:** Other - {selected_quote['referral_other']}")
                    else:
                        st.write(f"**Referral Source:** {selected_quote['referral_source']}")
                
            with col2:
                st.markdown("### Property Information")
                st.write(f"**Region:** {selected_quote['region']}")
                st.write(f"**Property Size:** {selected_quote['property_size']}")
                st.write(f"**Bathrooms:** {selected_quote['num_bathrooms']}")
                st.write(f"**Reception Rooms:** {selected_quote['num_reception_rooms']}")
                
            with col3:
                st.markdown("### Service Information")
                st.write(f"**Service Type:** {selected_quote['service_type']}")
                st.write(f"**Cleaning Date:** {selected_quote['cleaning_date']}")
                
                # Display time preference if available
                if 'time_preference' in selected_quote and selected_quote['time_preference']:
                    st.write(f"**Time Slot:** {selected_quote['time_preference']}")
                
                st.write(f"**Status:** {selected_quote['status']}")
                # Format timestamp to UK date format (DD/MM/YYYY) with HH:MM time format
                created_date = pd.to_datetime(selected_quote['timestamp'])
                st.write(f"**Created:** {created_date.strftime('%d/%m/%Y %H:%M')}")
                
                # Show cleaner preference if one was selected (not 'No Preference')
                if 'cleaner_preference' in selected_quote and selected_quote['cleaner_preference'] != 'No Preference':
                    st.write(f"**Cleaner Preference:** {selected_quote['cleaner_preference']}")
            
            # Additional services section
            st.markdown("### Additional Services")
            
            additional_services = []
            if selected_quote["oven_clean"]:
                additional_services.append("Oven Clean")
            if selected_quote["carpet_cleaning"]:
                additional_services.append(f"Carpet Cleaning ({selected_quote['carpet_rooms']} rooms)")
            if selected_quote["internal_windows"]:
                additional_services.append("Internal Windows")
            if selected_quote["external_windows"]:
                additional_services.append("External Windows")
            if selected_quote["balcony_patio"]:
                additional_services.append("Sweep Balcony/Patio")
            
            if additional_services:
                for service in additional_services:
                    st.write(f"- {service}")
            else:
                st.write("No additional services selected")
                
            if selected_quote["cleaning_materials"]:
                st.write("- Cleaning Materials Included")
            
            # Price details section
            st.markdown("### Price Details")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Base Price:** £{selected_quote['base_price']:.2f}")
                
                if selected_quote["extra_bathrooms_cost"] > 0:
                    st.write(f"**Extra Bathrooms:** £{selected_quote['extra_bathrooms_cost']:.2f}")
                
                if selected_quote["extra_reception_cost"] > 0:
                    st.write(f"**Extra Reception Rooms:** £{selected_quote['extra_reception_cost']:.2f}")
                
                if selected_quote["additional_services_cost"] > 0:
                    st.write(f"**Additional Services:** £{selected_quote['additional_services_cost']:.2f}")
                
                if selected_quote["materials_cost"] > 0:
                    st.write(f"**Cleaning Materials:** £{selected_quote['materials_cost']:.2f}")
                
            with col2:
                st.write(f"**Hourly Rate:** £{selected_quote['hourly_rate']:.2f}")
                # Format hours required to 2 decimal places
                hours_required = float(selected_quote['hours_required'])
                st.write(f"**Hours Required:** {hours_required:.2f}")
                st.write(f"**Cleaners Required:** {selected_quote['cleaners_required']}")
                st.write(f"**Region Multiplier:** {selected_quote['region_multiplier']:.2f}")
                st.write(f"**Markup ({selected_quote['markup_percentage']}%):** £{selected_quote['markup']:.2f}")
                
            # Handle price display (could be string or float/numpy value)
            try:
                # First try handling it as a string (with pound sign)
                price_value = float(str(selected_quote['total_price']).replace('£', ''))
                st.markdown(f"### Total Price: £{price_value:.2f}")
            except:
                # If that fails, try handling it as a numeric value
                try:
                    price_value = float(selected_quote['total_price'])
                    st.markdown(f"### Total Price: £{price_value:.2f}")
                except:
                    # Last resort fallback
                    st.markdown(f"### Total Price: {selected_quote['total_price']}")
            
            # Quote actions
            st.markdown("### Actions")
            
            col1, col2, col3 = st.columns(3)
            
            current_status = selected_quote["status"]
            
            with col1:
                if current_status != "Scheduled":
                    # Create a custom button that looks like the primary button and toggles content
                    show_scheduling = st.button("Schedule Cleaning\n\n(After Contractor Confirmation)", 
                                              key="show_schedule_btn", 
                                              type="primary")
                    
                    if show_scheduling:
                        st.session_state.show_scheduling_section = True
                    
                    # Initialize the session state for showing scheduling section if not exists
                    if 'show_scheduling_section' not in st.session_state:
                        st.session_state.show_scheduling_section = False
                    
                    # Show the scheduling section if the button was clicked
                    if st.session_state.show_scheduling_section:
                        st.info("⚠️ Only schedule after confirming contractor availability. This will mark the quote as confirmed in the system.")
                        
                        # Contractor availability confirmation
                        availability_confirmed = st.checkbox("I have confirmed contractor availability for this date", key="availability_confirmed")
                        
                        # Date picker for contractor availability in UK format
                        available_date = st.date_input("Confirmed cleaning date:", 
                                                     value=None, 
                                                     key="schedule_date",
                                                     format="DD/MM/YYYY")  # UK date format
                        
                        # Get cleaning hours and cleaners required
                        hours_required = selected_quote["hours_required"]
                        current_cleaners = selected_quote["cleaners_required"]
                        
                        # Cleaner options
                        st.write("### Cleaner Options")
                        st.write(f"Currently calculated: {current_cleaners} cleaner(s) for {float(hours_required):.2f} hours")
                        
                        cleaner_options = []
                        if hours_required <= 6:  # Only show options for reasonable durations
                            # Calculate variations
                            for num_cleaners in range(1, 4):  # 1 to 3 cleaners
                                if num_cleaners == current_cleaners:
                                    # This is the default option
                                    time_needed = hours_required
                                else:
                                    # Recalculate time based on cleaners
                                    time_needed = (hours_required * current_cleaners) / num_cleaners
                                
                                # Only add reasonable options (don't show 0.5 hour jobs)
                                if time_needed >= 1.0:
                                    cleaner_options.append({
                                        "cleaners": num_cleaners,
                                        "hours": time_needed
                                    })
                        
                        # Create radio options
                        cleaner_radio_options = [
                            f"{opt['cleaners']} cleaner(s) for {opt['hours']:.2f} hours" 
                            for opt in cleaner_options
                        ]
                        
                        if cleaner_radio_options:
                            selected_cleaner_option = st.radio(
                                "Choose cleaner configuration:",
                                options=cleaner_radio_options,
                                index=next((i for i, opt in enumerate(cleaner_options) 
                                          if opt["cleaners"] == current_cleaners), 0)
                            )
                            
                            # Extract selected cleaners and hours
                            selected_index = cleaner_radio_options.index(selected_cleaner_option)
                            selected_cleaners = cleaner_options[selected_index]["cleaners"]
                            selected_hours = cleaner_options[selected_index]["hours"]
                            
                            # Show time preference options based on hours
                            st.write("### Time Slot")
                            if selected_hours > 3:
                                st.info("Due to the cleaning duration (over 3 hours), only morning slots are available.")
                                time_options = ["Morning (8AM-12PM)"]
                            else:
                                time_options = ["Morning (8AM-12PM)", "Afternoon (12PM-4PM)", "Evening (4PM-8PM)"]
                                
                            time_preference = st.selectbox("Confirmed time slot:", time_options, key="schedule_time")
                        else:
                            # Fallback if no options (shouldn't happen, but just in case)
                            st.error("Could not calculate cleaner options. Please contact support.")
                            selected_cleaners = current_cleaners
                            selected_hours = hours_required
                            time_options = ["Morning (8AM-12PM)", "Afternoon (12PM-4PM)", "Evening (4PM-8PM)"]
                            time_preference = st.selectbox("Confirmed time slot:", time_options, key="schedule_time")
                        
                        # Cleaner assignment
                        cleaner_name = st.text_input("Assigned cleaner(s):", key="cleaner_name", 
                                                    placeholder="Enter name(s) of assigned cleaner(s)")
                        
                        # Admin scheduling notes
                        admin_notes = st.text_area("Admin notes for scheduling:", key="admin_scheduling_notes", 
                                                placeholder="Enter special instructions, access details, cleaning priorities, etc.")
                        
                        # Add a button to hide the scheduling section
                        if st.button("Cancel", key="hide_schedule_btn"):
                            st.session_state.show_scheduling_section = False
                            st.rerun()
                            
                        # Confirm scheduling button
                        if availability_confirmed:
                            if st.button("Confirm Scheduling", key="schedule_btn", type="primary"):
                                # Update quote status to scheduled
                                update_quote_status(selected_quote_id, "Scheduled")
                                
                                # Get quote data
                                quote_data = get_quote_by_id(selected_quote_id)
                                if quote_data:
                                    # Update cleaning date and time in the database
                                    engine = get_db_connection()
                                    with engine.connect() as connection:
                                        stmt = update(Quote).where(Quote.quote_id == selected_quote_id).values(
                                            cleaning_date=str(available_date),
                                            time_preference=time_preference,
                                            admin_notes=admin_notes if admin_notes else quote_data.get("admin_notes")
                                        )
                                        connection.execute(stmt)
                                        connection.commit()
                                    
                                    # Update CSV file
                                    from utils.data_storage import update_csv_field
                                    update_csv_field(selected_quote_id, "cleaning_date", str(available_date))
                                    update_csv_field(selected_quote_id, "time_preference", time_preference)
                                    if admin_notes:
                                        update_csv_field(selected_quote_id, "admin_notes", admin_notes)
                                    
                                    # Store assigned cleaner if provided
                                    if cleaner_name:
                                        update_csv_field(selected_quote_id, "assigned_cleaner", cleaner_name)
                                        # Update database as well (this would require adding the field to the database schema)
                                        try:
                                            with engine.connect() as connection:
                                                stmt = update(Quote).where(Quote.quote_id == selected_quote_id).values(
                                                    assigned_cleaner=cleaner_name
                                                )
                                                connection.execute(stmt)
                                                connection.commit()
                                        except Exception as e:
                                            # If the column doesn't exist yet, just log the error
                                            print(f"Could not update assigned_cleaner in database: {str(e)}")
                                    
                                    # If this is an admin-created quote that hasn't been sent to the customer yet, 
                                    # ask if the admin wants to notify the customer now
                                    if quote_data.get("admin_created", False) and not quote_data.get("sent_to_customer", False):
                                        if st.checkbox("Notify customer of scheduled cleaning?", key="notify_customer"):
                                            # Format quote data for email
                                            formatted_quote = {
                                                "quote_id": quote_data["quote_id"],
                                                "status": "Scheduled",  # Updated status
                                                "customer_info": {
                                                    "name": quote_data["customer_name"],
                                                    "email": quote_data["customer_email"],
                                                    "phone": quote_data.get("customer_phone", "Not provided"),  # Add phone number
                                                    "address": quote_data["customer_address"],
                                                    "postcode": quote_data["customer_postcode"],
                                                    "referral_source": quote_data.get("referral_source"),
                                                    "referral_other": quote_data.get("referral_other")
                                                },
                                                "property_info": {
                                                    "region": quote_data["region"],
                                                    "property_size": quote_data["property_size"],
                                                    "num_bathrooms": quote_data["num_bathrooms"],
                                                    "num_reception_rooms": quote_data["num_reception_rooms"]
                                                },
                                                "service_info": {
                                                    "service_type": quote_data["service_type"],
                                                    "cleaning_date": str(available_date),  # Updated date
                                                    "time_preference": time_preference,  # Updated time
                                                    "cleanliness_level": quote_data.get("cleanliness_level"),
                                                    "pet_status": quote_data.get("pet_status"),
                                                    "cleaning_materials": quote_data["cleaning_materials"],
                                                    "additional_services": {
                                                        "oven_clean": quote_data["oven_clean"],
                                                        "carpet_cleaning": quote_data["carpet_cleaning"],
                                                        "carpet_rooms": quote_data["carpet_rooms"],
                                                        "internal_windows": quote_data["internal_windows"],
                                                        "external_windows": quote_data["external_windows"],
                                                        "balcony_patio": quote_data["balcony_patio"]
                                                    }
                                                },
                                                "price_details": {
                                                    "base_price": quote_data["base_price"],
                                                    "extra_bathrooms_cost": quote_data["extra_bathrooms_cost"],
                                                    "extra_reception_cost": quote_data["extra_reception_cost"],
                                                    "additional_services_cost": quote_data["additional_services_cost"],
                                                    "materials_cost": quote_data["materials_cost"],
                                                    "subtotal": quote_data["subtotal"],
                                                    "markup_percentage": quote_data["markup_percentage"],
                                                    "markup": quote_data["markup"],
                                                    "total_price": quote_data["total_price"],
                                                    "hourly_rate": quote_data["hourly_rate"],
                                                    "hours_required": quote_data["hours_required"],
                                                    "cleaners_required": quote_data["cleaners_required"],
                                                    "region_multiplier": quote_data["region_multiplier"]
                                                }
                                            }
                                            
                                            # Send email with scheduling information
                                            is_scheduled = True
                                            send_customer_email(formatted_quote, is_scheduled)
                                            
                                            # Update the sent_to_customer status
                                            update_sent_to_customer(selected_quote_id, True)
                                            st.success(f"Scheduling confirmation sent to {quote_data['customer_email']}.")
                                    
                                    # Success message
                                    st.success(f"Quote {selected_quote_id} scheduled for {available_date} in the {time_preference.split()[0].lower()}.")
                                    st.rerun()
                        else:
                            st.error("Please confirm contractor availability before scheduling")
            
            with col2:
                if current_status != "Completed":
                    if st.button("Mark as Completed", key="complete_btn", type="primary"):
                        update_quote_status(selected_quote_id, "Completed")
                        st.success(f"Quote {selected_quote_id} marked as Completed.")
                        st.rerun()
            
            with col3:
                if current_status != "Cancelled":
                    if st.button("Mark as Cancelled", key="cancel_btn", type="primary"):
                        update_quote_status(selected_quote_id, "Cancelled")
                        st.success(f"Quote {selected_quote_id} marked as Cancelled.")
                        st.rerun()
            
            # Always show the "Send Quote" button for admin actions
            st.markdown("### Admin Quote Actions")
            
            # Show a different message based on whether the quote has been sent
            if not selected_quote["sent_to_customer"]:
                st.warning("This quote has not been sent to the customer yet.")
            else:
                st.info("This quote has been sent to the customer. You can send it again if needed.")
            
            # Email destinations - always show these options
            col1, col2 = st.columns(2)
            with col1:
                send_to_customer = st.checkbox("Send to customer", value=True)
            with col2:
                send_to_business = st.checkbox("Send copy to business email", value=True)
            
            if not send_to_customer and not send_to_business:
                st.error("You must select at least one email recipient")
                send_btn_disabled = True
            else:
                send_btn_disabled = False
            
            if send_to_customer and send_to_business:
                button_label = "Send Quote to Customer & Business"
            elif send_to_customer:
                button_label = "Send Quote to Customer"
            elif send_to_business:
                button_label = "Send Quote to Business"
            else:
                button_label = "Send Quote"
            
            if not send_btn_disabled and st.button(button_label, key="send_to_customer_btn", type="primary"):
                # Get the full quote data
                quote_data = get_quote_by_id(selected_quote_id)
                
                # Add debug to see exactly what's in the data
                print(f"DEBUG - Raw quote data for {selected_quote_id}:")
                if quote_data:
                    for key, value in quote_data.items():
                        print(f"  {key}: {value}")
                else:
                    print("  No data found - quote_data is None")
                
                if quote_data:
                    # Convert the dictionary to the structured format expected by email_service
                    formatted_quote = {
                        "quote_id": quote_data["quote_id"],
                        "status": quote_data["status"],
                        "customer_info": {
                            "name": quote_data["customer_name"],
                            "email": quote_data["customer_email"],
                            "phone": quote_data.get("customer_phone", "Not provided"),  # Add phone number
                            "address": quote_data["customer_address"],
                            "postcode": quote_data["customer_postcode"],
                            "referral_source": quote_data.get("referral_source"),
                            "referral_other": quote_data.get("referral_other")
                        },
                        "property_info": {
                            "region": quote_data["region"],
                            "property_size": quote_data["property_size"],
                            "num_bathrooms": quote_data["num_bathrooms"],
                            "num_reception_rooms": quote_data["num_reception_rooms"]
                        },
                        "service_info": {
                            "service_type": quote_data["service_type"],
                            "cleaning_date": quote_data["cleaning_date"],
                            "time_preference": quote_data.get("time_preference"),
                            "cleanliness_level": quote_data.get("cleanliness_level"),
                            "pet_status": quote_data.get("pet_status"),
                            "cleaning_materials": quote_data["cleaning_materials"],
                            "additional_services": {
                                "oven_clean": quote_data["oven_clean"],
                                "carpet_cleaning": quote_data["carpet_cleaning"],
                                "carpet_rooms": quote_data["carpet_rooms"],
                                "internal_windows": quote_data["internal_windows"],
                                "external_windows": quote_data["external_windows"],
                                "balcony_patio": quote_data["balcony_patio"]
                            }
                        },
                        "price_details": {
                            "base_price": quote_data["base_price"],
                            "extra_bathrooms_cost": quote_data["extra_bathrooms_cost"],
                            "extra_reception_cost": quote_data["extra_reception_cost"],
                            "additional_services_cost": quote_data["additional_services_cost"],
                            "materials_cost": quote_data["materials_cost"],
                            "subtotal": quote_data["subtotal"],
                            "markup_percentage": quote_data["markup_percentage"],
                            "markup": quote_data["markup"],
                            "total_price": quote_data["total_price"],
                            "hourly_rate": quote_data["hourly_rate"],
                            "hours_required": quote_data["hours_required"],
                            "cleaners_required": quote_data["cleaners_required"],
                            "region_multiplier": quote_data["region_multiplier"]
                        }
                    }
                    
                    # Send the quote based on selected destinations
                    is_scheduled = (quote_data["status"] == "Scheduled")
                    success_messages = []
                    
                    # Import email functions
                    from utils.email_service import send_customer_email, send_business_email
                    
                    # Verify that formatted_quote has all the required information for emails
                    print("VERIFICATION - Formatted quote data before sending emails:")
                    print(f"  Quote ID: {formatted_quote.get('quote_id')}")
                    print(f"  Customer Name: {formatted_quote.get('customer_info', {}).get('name')}")
                    print(f"  Customer Email: {formatted_quote.get('customer_info', {}).get('email')}")
                    print(f"  Property Size: {formatted_quote.get('property_info', {}).get('property_size')}")
                    print(f"  Service Type: {formatted_quote.get('service_info', {}).get('service_type')}")
                    print(f"  Total Price: £{formatted_quote.get('price_details', {}).get('total_price')}")
                    
                    # Add very detailed debugging of all fields
                    print("\nDETAILED DEBUG - Complete formatted quote structure:")
                    for section_key, section_data in formatted_quote.items():
                        print(f"Section: {section_key}")
                        if isinstance(section_data, dict):
                            for field_key, field_value in section_data.items():
                                print(f"  {field_key}: {field_value}")
                        else:
                            print(f"  Value: {section_data}")
                    
                    if send_to_customer:
                        # Use is_admin_sending=True to trigger the proper email template with pricing and T&C
                        send_customer_email(formatted_quote, is_scheduled, is_admin_sending=True)
                        success_messages.append(f"Quote sent to customer ({quote_data['customer_email']})")
                        # Update sent_to_customer status in database and CSV
                        update_sent_to_customer(selected_quote_id, True)
                        # Update status to "Quoted" when sent to customer
                        update_quote_status(selected_quote_id, "Quoted")
                    
                    if send_to_business:
                        send_business_email(formatted_quote, is_scheduled, is_admin_sending=True)
                        success_messages.append("Copy sent to business email")
                    
                    # Display success message(s)
                    st.success(f"Quote {selected_quote_id}: {' and '.join(success_messages)}.")
                else:
                    st.error(f"Could not retrieve quote data for {selected_quote_id}.")
                        
except Exception as e:
    st.error(f"Error retrieving quotes: {str(e)}")