import os
import json
import re
from datetime import datetime
from utils.config import load_config

def format_date_uk(date_str):
    """Convert date from YYYY-MM-DD to DD/MM/YYYY format"""
    try:
        # Try to parse the date string
        if isinstance(date_str, str) and re.match(r'^\d{4}-\d{2}-\d{2}$', date_str):
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            return date_obj.strftime('%d/%m/%Y')
        return date_str  # Return original if not in expected format
    except:
        return date_str  # Return original on any error

def create_customer_email_content(quote_data, is_scheduled=False):
    """Create customer email content with quote details"""
    from utils.pricing import load_pricing_config
    
    config = load_config()
    company_name = config["company_name"]
    company_website = config.get("company_website", "www.kmiservices.co.uk")
    
    # Load pricing config for extra_costs if needed
    price_details = quote_data["price_details"]
    if "extra_costs" not in price_details:
        print("Loading pricing config for extra_costs in customer email content")
        pricing_config = load_pricing_config()
        price_details["extra_costs"] = pricing_config["extra_costs"]
    
    # Extract data with debug logs to trace issues
    customer_name = quote_data["customer_info"]["name"]
    service_type = quote_data["service_info"]["service_type"]
    # Format date in UK format (DD/MM/YYYY)
    cleaning_date = format_date_uk(quote_data["service_info"]["cleaning_date"])
    property_size = quote_data["property_info"]["property_size"]
    # Format the total price to display only 2 decimal places
    total_price = "{:.2f}".format(price_details["total_price"])
    # Make sure we format all price values to 2 decimal places
    formatted_total_price = total_price  # Already formatted above
    hours_required = price_details["hours_required"]
    quote_id = quote_data.get("quote_id", "N/A")
    
    # Print debug info for price values
    print(f"PRICE DEBUG - Raw total_price: {quote_data['price_details']['total_price']}, Formatted: {formatted_total_price}")
    
    # Print debug information to track data flow
    print(f"Customer Email Data - Name: {customer_name}, ID: {quote_id}, Property: {property_size}, Service: {service_type}, Price: £{total_price}")
    
    # Create scheduled message
    time_preference_text = ""
    if is_scheduled and quote_data["service_info"].get("time_preference"):
        time_preference = quote_data["service_info"].get("time_preference", "morning").split()[0].lower()
        time_preference_text = " in the " + time_preference
    
    scheduled_msg = "This cleaning has been scheduled for " + cleaning_date + time_preference_text + "." if is_scheduled else ""
    
    # Email subject
    subject = "Your " + company_name + " Cleaning Quote" if not is_scheduled else "Your " + company_name + " Cleaning Booking Confirmation"
    
    # Start building HTML content
    html_content = """
    <html>
    <head>
        <style>
            body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
            .container { max-width: 600px; margin: 0 auto; padding: 20px; }
            h1 { color: #22C7D6; }
            h2 { color: #22C7D6; }
            .quote-summary { background-color: #f9f9f9; padding: 15px; border-radius: 5px; margin-bottom: 20px; }
            .price { font-size: 24px; font-weight: bold; color: #22C7D6; }
            .footer { margin-top: 30px; font-size: 12px; color: #777; text-align: center; }
        </style>
    </head>
    <body>
        <div class="container">
    """
    
    # Add header
    html_content += "<h1>" + ("Your Quote Details" if not is_scheduled else "Your Scheduled Cleaning") + "</h1>"
    
    # Add greeting
    html_content += "<p>Dear " + customer_name + ",</p>"
    
    # Add intro
    if not is_scheduled:
        html_content += "<p>Thank you for your enquiry with " + company_name + ". Here are the details of your quote:</p>"
    else:
        html_content += "<p>Thank you for booking your clean with " + company_name + ". Here are the details of your scheduled cleaning:</p>"
    
    # Add quote summary
    html_content += """
        <div class="quote-summary">
            <h2>Quote Summary (ID: """ + quote_id + """)</h2>
            <p><strong>Name:</strong> """ + customer_name + """</p>
            <p><strong>Phone:</strong> """ + quote_data["customer_info"].get("phone", "Not provided") + """</p>
            <p><strong>Service Type:</strong> """ + service_type + """</p>
            <p><strong>Property Size:</strong> """ + property_size + """</p>
            <p><strong>Cleaning Date:</strong> """ + cleaning_date + """</p>
            <p><strong>Property Details:</strong> """ + str(quote_data["property_info"]["num_bathrooms"]) + """ bathroom(s), """ + str(quote_data["property_info"]["num_reception_rooms"]) + """ reception room(s)</p>
            <p><strong>Cleanliness Level:</strong> """ + quote_data["service_info"].get("cleanliness_level", "Normal") + """</p>
            <p><strong>Pets:</strong> """ + quote_data["service_info"].get("pet_status", "No Pets") + """</p>
            <p><strong>Cleaner Preference:</strong> """ + quote_data["service_info"].get("cleaner_preference", "No Preference") + """</p>
    """
    
    # Add customer notes to the summary if provided
    if quote_data["service_info"].get("customer_notes"):
        html_content += "<p><strong>Your Notes:</strong> " + quote_data["service_info"]["customer_notes"] + """</p>
    """
    
    # Add time preference if scheduled
    if is_scheduled and quote_data["service_info"].get("time_preference"):
        html_content += "<p><strong>Preferred Time:</strong> " + quote_data["service_info"].get("time_preference", "Not specified") + "</p>"
    
    # Add time and cleaner details
    # Make sure hours are formatted with 2 decimal places
    formatted_hours = "{:.2f}".format(float(hours_required))
    html_content += "<p><strong>Time Required:</strong> " + formatted_hours + " hours</p>"
    html_content += "<p><strong>Cleaners Required:</strong> " + str(quote_data["price_details"]["cleaners_required"]) + "</p>"
    
    # Add note about cleaner preference if not "No Preference"
    cleaner_preference = quote_data["service_info"].get("cleaner_preference", "No Preference")
    if cleaner_preference != "No Preference":
        html_content += "<p><em>Note: Cleaner preference affects time but not price. More cleaners = shorter duration.</em></p>"
    
    html_content += "<p><strong>Total Price:</strong> <span class=\"price\">&pound;" + "{:.2f}".format(float(total_price)) + "</span></p>"
    
    # Add additional services if any
    additional_services = quote_data["service_info"]["additional_services"]
    if any(additional_services.values()):
        html_content += "<h3>Additional Services:</h3><ul>"
        
        if additional_services["oven_clean"]:
            html_content += "<li>Oven Clean</li>"
            
        if additional_services["carpet_cleaning"]:
            carpet_rooms = additional_services["carpet_rooms"]
            if carpet_rooms > 1:
                html_content += "<li>Carpet Cleaning (" + str(carpet_rooms) + " rooms)</li>"
            else:
                html_content += "<li>Carpet Cleaning (1 room)</li>"
            
        if additional_services["internal_windows"]:
            html_content += "<li>Internal Windows</li>"
            
        if additional_services["external_windows"]:
            html_content += "<li>External Windows</li>"
            
        if additional_services["balcony_patio"]:
            html_content += "<li>Sweep Balcony/Patio</li>"
            
        html_content += "</ul>"
    
    # Add cleaning materials if included
    if quote_data["service_info"]["cleaning_materials"]:
        html_content += "<p><strong>Cleaning Materials:</strong> Included</p>"
    
    # Add closing content based on scheduled or not
    if is_scheduled:
        html_content += "</div>"
        html_content += "<p>Our cleaning team will arrive on " + cleaning_date + time_preference_text + " to perform your " + service_type.lower() + ". If you need to make any changes to your booking, please contact us as soon as possible.</p>"
        
        # Add note for long cleanings
        if quote_data["price_details"]["hours_required"] > 3:
            html_content += "<p>Please note: Due to the estimated cleaning time of " + "{:.2f}".format(float(quote_data["price_details"]["hours_required"])) + " hours, this cleaning could only be scheduled in the morning.</p>"
        
        # Add customer notes if any
        if quote_data["service_info"].get("customer_notes"):
            html_content += "<p><strong>Your notes for our cleaning team:</strong> " + quote_data["service_info"]["customer_notes"] + "</p>"
        
        html_content += """
            <p>If you have any questions or special requirements, please don't hesitate to contact us.</p>
            <p>Thank you for choosing """ + company_name + """!</p>
            <p>Best regards,<br>The """ + company_name + """ Team</p>
        """
    else:
        html_content += "</div>"
        
        # Add scheduling button/link
        scheduling_url = f"https://kmiservices.co.uk/schedule?quote_id={quote_id}"
        
        html_content += f"""
            <p>This quote is valid for 30 days.</p>
            <div style="text-align: center; margin: 20px 0;">
                <a href="{scheduling_url}" style="display: inline-block; background-color: #22C7D6; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; font-weight: bold; font-size: 16px;">Request Cleaning Date</a>
            </div>
            <p>This will allow you to request your preferred cleaning date and time. We'll confirm availability with our cleaning team and contact you to finalize your booking.</p>
            <p>You can also request a booking by replying to this email or calling us directly.</p>
            <p>If you have any questions or special requirements, please don't hesitate to contact us.</p>
            <p>Thank you for considering """ + company_name + """!</p>
            <p>Best regards,<br>The """ + company_name + """ Team</p>
        """
    
    # Add footer
    html_content += """
            <div class="footer">
                <p>""" + company_name + """ | """ + company_website + """</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return subject, html_content

def create_business_email_content(quote_data, is_scheduled=False):
    """Create detailed business email content with all quote details including business sensitive data"""
    from utils.pricing import load_pricing_config
    
    config = load_config()
    company_name = config["company_name"]
    
    # Debug log for business email price
    if "price_details" in quote_data and "total_price" in quote_data["price_details"]:
        print(f"BUSINESS EMAIL CONTENT - Total price: {quote_data['price_details']['total_price']}")
    
    # Load pricing config for extra_costs if needed
    price_details = quote_data["price_details"]
    if "extra_costs" not in price_details:
        print("Loading pricing config for extra_costs")
        pricing_config = load_pricing_config()
        price_details["extra_costs"] = pricing_config["extra_costs"]
    
    customer_name = quote_data["customer_info"]["name"]
    customer_email = quote_data["customer_info"]["email"]
    customer_phone = quote_data["customer_info"].get("phone", "Not provided")  # Explicitly get phone
    customer_address = quote_data["customer_info"]["address"]
    customer_postcode = quote_data["customer_info"]["postcode"]
    
    service_type = quote_data["service_info"]["service_type"]
    # Format date in UK format (DD/MM/YYYY)
    cleaning_date = format_date_uk(quote_data["service_info"]["cleaning_date"])
    property_size = quote_data["property_info"]["property_size"]
    region = quote_data["property_info"]["region"]
    num_bathrooms = quote_data["property_info"]["num_bathrooms"]
    num_reception_rooms = quote_data["property_info"]["num_reception_rooms"]
    
    # Use the price_details variable that was already defined above
    hourly_rate = price_details["hourly_rate"]
    hours_required = price_details["hours_required"]
    cleaners_required = price_details["cleaners_required"]
    region_multiplier = price_details["region_multiplier"]
    
    base_price = price_details["base_price"]
    extra_bathrooms_cost = price_details["extra_bathrooms_cost"]
    extra_reception_cost = price_details["extra_reception_cost"]
    additional_services_cost = price_details["additional_services_cost"]
    materials_cost = price_details["materials_cost"]
    subtotal = price_details["subtotal"]
    markup_percentage = price_details["markup_percentage"]
    markup = price_details["markup"]
    total_price = price_details["total_price"]
    
    quote_id = quote_data.get("quote_id", "N/A")
    
    # Create scheduled message
    time_preference_text = ""
    if is_scheduled and quote_data["service_info"].get("time_preference"):
        time_preference = quote_data["service_info"].get("time_preference", "morning").split()[0].lower()
        time_preference_text = " in the " + time_preference
    
    scheduled_msg = "This cleaning has been scheduled for " + cleaning_date + time_preference_text + "." if is_scheduled else ""
    
    # Email subject
    action_type = "Scheduled Cleaning" if is_scheduled else "New Quote"
    # Ensure we have valid data for the email - add debug logs
    print(f"Business Email Data - Customer: {customer_name}, Property: {property_size}, Service: {service_type}, ID: {quote_id}")
    
    # Create subject line without phone number to avoid empty parentheses
    subject = "[BUSINESS] " + action_type + " - " + customer_name + " - " + property_size + " - " + service_type + " (ID: " + quote_id + ")"
    
    # Start building HTML content
    html_content = """
    <html>
    <head>
        <style>
            body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
            .container { max-width: 800px; margin: 0 auto; padding: 20px; }
            h1 { color: #22C7D6; }
            h2 { color: #22C7D6; }
            .section { background-color: #f9f9f9; padding: 15px; border-radius: 5px; margin-bottom: 20px; }
            .price-breakdown { width: 100%; border-collapse: collapse; margin-top: 15px; }
            .price-breakdown th, .price-breakdown td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            .price-breakdown th { background-color: #f2f2f2; }
            .total-row { font-weight: bold; background-color: #e3f7f9; }
            .footer { margin-top: 30px; font-size: 12px; color: #777; text-align: center; }
        </style>
    </head>
    <body>
        <div class="container">
    """
    
    # Add header
    if is_scheduled:
        html_content += "<h1>[SCHEDULED] Cleaning Quote Details - BUSINESS VIEW</h1>"
    else:
        html_content += "<h1>Cleaning Quote Details - BUSINESS VIEW</h1>"
    
    # Customer information section
    html_content += """
        <div class="section">
            <h2>Customer Information</h2>
            <p><strong>Name:</strong> """ + customer_name + """</p>
            <p><strong>Email:</strong> """ + customer_email + """</p>
            <p><strong>Phone:</strong> """ + quote_data["customer_info"].get("phone", "Not provided") + """</p>
            <p><strong>Address:</strong> """ + customer_address + """</p>
            <p><strong>Postcode:</strong> """ + customer_postcode + """</p>
            <p><strong>Quote ID:</strong> """ + quote_id + """</p>
        </div>
    """
    
    # Property & Service information
    html_content += """
        <div class="section">
            <h2>Property & Service Information</h2>
            <p><strong>Region:</strong> """ + region + """</p>
            <p><strong>Property Size:</strong> """ + property_size + """</p>
            <p><strong>Bathrooms:</strong> """ + str(num_bathrooms) + """</p>
            <p><strong>Reception Rooms:</strong> """ + str(num_reception_rooms) + """</p>
            <p><strong>Service Type:</strong> """ + service_type + """</p>
            <p><strong>Cleaning Date:</strong> """ + cleaning_date + """</p>
    """
    
    # Add time preference if scheduled
    if is_scheduled and quote_data["service_info"].get("time_preference"):
        html_content += "<p><strong>Preferred Time:</strong> " + quote_data["service_info"].get("time_preference", "Not specified") + "</p>"
    
    # Add cleanliness level and pet status
    html_content += "<p><strong>Cleanliness Level:</strong> " + quote_data["service_info"].get("cleanliness_level", "Normal") + "</p>"
    html_content += "<p><strong>Pets in Home:</strong> " + quote_data["service_info"].get("pet_status", "No Pets") + "</p>"
    
    # Add cleaner preference if one was selected
    cleaner_preference = quote_data["service_info"].get("cleaner_preference", "No Preference")
    if cleaner_preference != "No Preference":
        html_content += "<p><strong>Cleaner Preference:</strong> " + cleaner_preference + "</p>"
        html_content += "<p><em>Note: Customer selected a cleaner preference. This affects job duration but not the total price.</em></p>"
    
    # Add customer notes if any
    if quote_data["service_info"].get("customer_notes"):
        html_content += "<p><strong>Customer Notes:</strong> " + quote_data["service_info"]["customer_notes"] + "</p>"
    
    # Add additional services if any
    additional_services = quote_data["service_info"]["additional_services"]
    if any(additional_services.values()) or quote_data["service_info"]["cleaning_materials"]:
        html_content += "<h3>Additional Services:</h3><ul>"
        
        if additional_services["oven_clean"]:
            html_content += "<li>Oven Clean</li>"
            
        if additional_services["carpet_cleaning"]:
            carpet_rooms = additional_services["carpet_rooms"]
            if carpet_rooms > 1:
                html_content += "<li>Carpet Cleaning (" + str(carpet_rooms) + " rooms)</li>"
            else:
                html_content += "<li>Carpet Cleaning (1 room)</li>"
            
        if additional_services["internal_windows"]:
            html_content += "<li>Internal Windows</li>"
            
        if additional_services["external_windows"]:
            html_content += "<li>External Windows</li>"
            
        if additional_services["balcony_patio"]:
            html_content += "<li>Sweep Balcony/Patio</li>"
        
        if quote_data["service_info"]["cleaning_materials"]:
            html_content += "<li>Cleaning Materials Included</li>"
            
        html_content += "</ul>"
    
    # Close the property and service section
    html_content += "</div>"
    
    # Business calculations section
    html_content += """
        <div class="section">
            <h2>Business Calculations</h2>
            <p><strong>Hourly Rate:</strong> &pound;""" + "{:.2f}".format(float(hourly_rate)) + """</p>
            <p><strong>Hours Required:</strong> """ + "{:.2f}".format(float(hours_required)) + """ hours</p>
            <p><strong>Cleaners Required:</strong> """ + str(cleaners_required) + """</p>
            <p><strong>Region Multiplier:</strong> """ + "{:.2f}".format(float(region_multiplier)) + """</p>
            
            <h3>Price Breakdown</h3>
            <table class="price-breakdown">
                <tr>
                    <th>Item</th>
                    <th>Cost</th>
                </tr>
                <tr>
                    <td>Base Price</td>
                    <td>&pound;""" + "{:.2f}".format(float(base_price)) + """</td>
                </tr>
    """
    
    # Add extra bathroom costs if any
    if extra_bathrooms_cost > 0:
        html_content += """
                <tr>
                    <td>Extra Bathrooms</td>
                    <td>&pound;""" + "{:.2f}".format(float(extra_bathrooms_cost)) + """</td>
                </tr>
        """
    
    # Add extra reception costs if any
    if extra_reception_cost > 0:
        html_content += """
                <tr>
                    <td>Extra Reception Rooms</td>
                    <td>&pound;""" + "{:.2f}".format(float(extra_reception_cost)) + """</td>
                </tr>
        """
    
    # Add oven cleaning cost if selected
    if additional_services["oven_clean"]:
        oven_cost = price_details["extra_costs"]["oven_clean"]
        html_content += """
                <tr>
                    <td>Oven Clean</td>
                    <td>&pound;""" + "{:.2f}".format(float(oven_cost)) + """</td>
                </tr>
        """
    
    # Add carpet cleaning cost if selected
    if additional_services["carpet_cleaning"]:
        carpet_cost = price_details["extra_costs"]["carpet_cleaning_per_room"] * additional_services["carpet_rooms"]
        html_content += """
                <tr>
                    <td>Carpet Cleaning (""" + str(additional_services["carpet_rooms"]) + """ rooms)</td>
                    <td>&pound;""" + "{:.2f}".format(float(carpet_cost)) + """</td>
                </tr>
        """
    
    # Add internal windows cost if selected
    if additional_services["internal_windows"]:
        internal_windows_cost = price_details["extra_costs"]["internal_windows"]
        html_content += """
                <tr>
                    <td>Internal Windows</td>
                    <td>&pound;""" + "{:.2f}".format(float(internal_windows_cost)) + """</td>
                </tr>
        """
    
    # Add external windows cost if selected
    if additional_services["external_windows"]:
        external_windows_cost = price_details["extra_costs"]["external_windows"]
        html_content += """
                <tr>
                    <td>External Windows</td>
                    <td>&pound;""" + "{:.2f}".format(float(external_windows_cost)) + """</td>
                </tr>
        """
    
    # Add balcony/patio cost if selected
    if additional_services["balcony_patio"]:
        balcony_cost = price_details["extra_costs"]["balcony_patio"]
        html_content += """
                <tr>
                    <td>Sweep Balcony/Patio</td>
                    <td>&pound;""" + "{:.2f}".format(float(balcony_cost)) + """</td>
                </tr>
        """
    
    # Add materials cost if included
    if materials_cost > 0:
        html_content += """
                <tr>
                    <td>Cleaning Materials</td>
                    <td>&pound;""" + "{:.2f}".format(float(materials_cost)) + """</td>
                </tr>
        """
    
    # Complete the price breakdown table
    html_content += """
                <tr>
                    <td>Subtotal</td>
                    <td>&pound;""" + "{:.2f}".format(float(subtotal)) + """</td>
                </tr>
                <tr>
                    <td>Markup (""" + str(markup_percentage) + """%)</td>
                    <td>&pound;""" + "{:.2f}".format(float(markup)) + """</td>
                </tr>
                <tr class="total-row">
                    <td>Total Price</td>
                    <td>&pound;""" + "{:.2f}".format(float(total_price)) + """</td>
                </tr>
            </table>
        </div>
    """
    
    # Admin adjustments section if applicable
    has_admin_adjustments = any(key in price_details and price_details[key] for key in ["admin_notes", "regular_client_discount_percentage", "original_cleaners", "original_markup_percentage"])
    
    if has_admin_adjustments:
        html_content += """
        <div class="section admin-section">
            <h2 style="color: #e74c3c;">Admin Adjustments</h2>
        """
        
        # Admin notes if any
        if "admin_notes" in price_details and price_details["admin_notes"]:
            html_content += "<p><strong>Admin Notes:</strong> " + price_details['admin_notes'] + "</p>"
        
        # Regular client discount if applied
        if "regular_client_discount_percentage" in price_details and price_details["regular_client_discount_percentage"]:
            html_content += """
            <div class="adjustment-item">
                <h3>Regular Client Discount</h3>
                <p><strong>Discount Percentage:</strong> """ + str(price_details['regular_client_discount_percentage']) + """%</p>
                <p><strong>Discount Amount:</strong> &pound;""" + "{:.2f}".format(float(price_details['regular_client_discount_amount'])) + """</p>
                <p><strong>Original Price:</strong> &pound;""" + "{:.2f}".format(float(price_details['original_price'])) + """</p>
                <p><strong>Discounted Price:</strong> &pound;""" + "{:.2f}".format(float(price_details['total_price'])) + """</p>
            </div>
            """
        
        # Cleaner adjustment if applied
        if "original_cleaners" in price_details and price_details["original_cleaners"]:
            html_content += """
            <div class="adjustment-item">
                <h3>Cleaner Adjustment</h3>
                <p><strong>Original Cleaners:</strong> """ + str(price_details['original_cleaners']) + """</p>
                <p><strong>Adjusted Cleaners:</strong> """ + str(price_details['cleaners_required']) + """</p>
                <p><strong>Original Hours:</strong> """ + "{:.2f}".format(float(price_details['original_hours'])) + """</p>
                <p><strong>Adjusted Hours:</strong> """ + "{:.2f}".format(float(price_details['hours_required'])) + """</p>
            </div>
            """
        
        # Markup adjustment if applied
        if "original_markup_percentage" in price_details and price_details["original_markup_percentage"]:
            html_content += """
            <div class="adjustment-item">
                <h3>Markup Adjustment</h3>
                <p><strong>Original Markup:</strong> """ + str(price_details['original_markup_percentage']) + """% (&pound;""" + "{:.2f}".format(float(price_details['original_markup'])) + """)</p>
                <p><strong>Adjusted Markup:</strong> """ + str(price_details['markup_percentage']) + """% (&pound;""" + "{:.2f}".format(float(price_details['markup'])) + """)</p>
            </div>
            """
        
        html_content += "</div>"
    
    # Add scheduling information
    if is_scheduled:
        html_content += "<p>" + scheduled_msg + "</p>"
    else:
        html_content += "<p>This is a quote only. Customer will need to confirm booking.</p>"
    
    # Add morning-only note for long cleanings
    if is_scheduled and hours_required > 3:
        # Format hours with 2 decimal places
        formatted_hours = "{:.2f}".format(float(hours_required))
        html_content += "<p><strong>Note:</strong> Due to the estimated cleaning time of " + formatted_hours + " hours, this cleaning can only be performed in the morning.</p>"
    
    # Add footer
    html_content += """
            <div class="footer">
                <p>Internal Business Email - """ + company_name + """</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return subject, html_content

def send_email(to_email, subject, html_content, email_type="customer_quote", direct_phone=None):
    """
    Send an email using SMTP or EmailJS.
    
    This function tries to send an email using SMTP first (Gmail or other provider),
    and falls back to EmailJS if SMTP fails.
    
    Parameters:
    - to_email: Email address of the recipient
    - subject: Email subject line
    - html_content: HTML content of the email
    - email_type: Type of email to send (customer_quote, admin_quote, customer_schedule, admin_schedule)
    - direct_phone: Phone number to use directly instead of extracting from HTML
    """
    # Enhanced debugging for EmailJS
    print(f"DEBUG: ------------ EMAIL DEBUG START ------------")
    print(f"DEBUG: Email type: {email_type}")
    print(f"DEBUG: Subject: {subject}")
    # Print debug info about the email content
    print(f"DEBUG: Sending email type: {email_type}")
    print(f"DEBUG: Subject: {subject}")
    print(f"DEBUG: To: {to_email}")
    # Print at least first 100 chars of content to check format
    content_preview = html_content[:100] + "..." if len(html_content) > 100 else html_content
    print(f"DEBUG: Content preview: {content_preview}")
    import requests
    import json
    import os
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    
    # Get email settings from config
    config = load_config()
    
    # For local development/testing mode with no email credentials, just print the email details
    if not os.environ.get('EMAIL_USER') and not os.environ.get('EMAILJS_USER_ID'):
        print("Sending email to: " + to_email)
        print("Subject: " + subject)
        print("Content length: " + str(len(html_content)) + " characters")
        return True
    
    # First try using SMTP (more reliable for server-side applications)
    if os.environ.get('EMAIL_USER') and os.environ.get('EMAIL_PASSWORD'):
        try:
            print("Trying to send email via SMTP...")
            # Get SMTP configuration from environment variables
            smtp_server = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
            smtp_port = int(os.environ.get('SMTP_PORT', 587))
            email_user = os.environ.get('EMAIL_USER')
            email_password = os.environ.get('EMAIL_PASSWORD')
            
            # Create message
            message = MIMEMultipart('alternative')
            message['Subject'] = subject
            message['From'] = email_user
            message['To'] = to_email
            
            # Attach HTML content
            html_part = MIMEText(html_content, 'html')
            message.attach(html_part)
            
            # Connect to server and send
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            # Make sure we have string values for login
            if email_user and email_password:
                server.login(str(email_user), str(email_password))
                server.sendmail(str(email_user), to_email, message.as_string())
            server.quit()
            
            print(f"Email sent to {to_email} successfully via SMTP!")
            return True
            
        except Exception as e:
            print(f"Error sending email via SMTP: {str(e)}")
            print("Falling back to EmailJS...")
    
    # Fall back to EmailJS if SMTP fails or is not configured
    if os.environ.get('EMAILJS_USER_ID'):
        try:
            # EmailJS credentials (store these securely in environment variables)
            emailjs_user_id = os.environ.get('EMAILJS_USER_ID')
            emailjs_service_id = os.environ.get('EMAILJS_SERVICE_ID')
            emailjs_private_key = os.environ.get('EMAILJS_PRIVATE_KEY')
            
            # Print environment variables for debugging (will be removed in production)
            print("DEBUG: Available environment variables:")
            print(f"Sending email type: {email_type}")
            print(f"EMAILJS_USER_ID exists: {bool(os.environ.get('EMAILJS_USER_ID'))}")
            print(f"EMAILJS_SERVICE_ID exists: {bool(os.environ.get('EMAILJS_SERVICE_ID'))}")
            print(f"EMAILJS_PRIVATE_KEY exists: {bool(os.environ.get('EMAILJS_PRIVATE_KEY'))}")
            
            # Check all possible template ID environment variables
            print(f"EMAILJS_TEMPLATE_ID exists: {bool(os.environ.get('EMAILJS_TEMPLATE_ID'))}")
            print(f"EMAILJS_CUSTOMER_QUOTE_TEMPLATE_ID exists: {bool(os.environ.get('EMAILJS_CUSTOMER_QUOTE_TEMPLATE_ID'))}")
            print(f"EMAILJS_ADMIN_QUOTE_TEMPLATE_ID exists: {bool(os.environ.get('EMAILJS_ADMIN_QUOTE_TEMPLATE_ID'))}")
            print(f"EMAILJS_CUSTOMER_SCHEDULE_TEMPLATE_ID exists: {bool(os.environ.get('EMAILJS_CUSTOMER_SCHEDULE_TEMPLATE_ID'))}")
            print(f"EMAILJS_ADMIN_SCHEDULE_TEMPLATE_ID exists: {bool(os.environ.get('EMAILJS_ADMIN_SCHEDULE_TEMPLATE_ID'))}")
            
            # Check which template we should use based on email_type
            template_var_name = f"EMAILJS_{email_type.upper()}_TEMPLATE_ID"
            print(f"Looking for environment variable: {template_var_name}")
            
            # Try to get the specific template ID using these fallbacks:
            # 1. Try the specific template ID for this email type
            # 2. If it's a full quote, fall back to the regular quote template
            # 3. Finally, use the generic template as last resort
            emailjs_template_id = None
            
            # Try the specific template first
            if os.environ.get(template_var_name):
                emailjs_template_id = os.environ.get(template_var_name)
            # For full quote templates, fall back to regular quote templates if not available
            elif email_type == "customer_full_quote" and os.environ.get('EMAILJS_CUSTOMER_QUOTE_TEMPLATE_ID'):
                print(f"Using customer_quote template as fallback for {email_type}")
                emailjs_template_id = os.environ.get('EMAILJS_CUSTOMER_QUOTE_TEMPLATE_ID')
            elif email_type == "admin_full_quote" and os.environ.get('EMAILJS_ADMIN_QUOTE_TEMPLATE_ID'):
                print(f"Using admin_quote template as fallback for {email_type}")
                emailjs_template_id = os.environ.get('EMAILJS_ADMIN_QUOTE_TEMPLATE_ID')
            # Lastly use the generic template ID
            else:
                emailjs_template_id = os.environ.get('EMAILJS_TEMPLATE_ID')
            
            if not emailjs_template_id:
                print(f"ERROR: No template ID found for {email_type}")
                print("Please add at least EMAILJS_TEMPLATE_ID to your Replit secrets")
                print("To find this ID, visit https://dashboard.emailjs.com/admin/templates")
                return False  # Return false instead of raising an exception
                
            if not emailjs_private_key:
                print(f"ERROR: EMAILJS_PRIVATE_KEY environment variable is not found")
                print("Please add EMAILJS_PRIVATE_KEY to your Replit secrets")
                print("This is required for server-side API calls with EmailJS Pro")
                print("To find this, visit https://dashboard.emailjs.com/admin/account")
                return False
            
            # Prepare the payload for EmailJS Pro (with private key for server-side calls)
            # Extract key details from the HTML content for direct template parameters
            import re
            
            # Try to extract customer name, property size, service type, and price from HTML
            # This ensures these key fields are available as direct template variables
            customer_name_match = re.search(r'<p><strong>Name:</strong>\s*([^<]+)</p>', html_content)
            customer_email_match = re.search(r'<p><strong>Email:</strong>\s*([^<]+)</p>', html_content)
            customer_phone_match = re.search(r'<p><strong>Phone:</strong>\s*([^<]+)</p>', html_content)
            property_size_match = re.search(r'<p><strong>Property Size:</strong>\s*([^<]+)</p>', html_content)
            service_type_match = re.search(r'<p><strong>Service Type:</strong>\s*([^<]+)</p>', html_content)
            cleaning_date_match = re.search(r'<p><strong>Cleaning Date:</strong>\s*([^<]+)</p>', html_content)
            # Updated pattern to extract just the number part, ignoring "hours" text
            hours_required_match = re.search(r'<p><strong>Time Required:</strong>\s*([0-9.]+)\s*hours?</p>', html_content)
            
            # Debug extracted fields, especially the phone and email
            print(f"DEBUG: Phone extraction - Pattern matched: {bool(customer_phone_match)}")
            if customer_phone_match:
                print(f"DEBUG: Extracted phone: '{customer_phone_match.group(1)}'")
            else:
                print(f"DEBUG: Phone pattern not found in HTML")
                # Print part of the HTML to help debug the issue
                phone_snippet = html_content[html_content.find("Phone"):html_content.find("Phone")+200] if "Phone" in html_content else "Phone field not found in HTML"
                print(f"DEBUG: HTML snippet around Phone: {phone_snippet}")
                
            print(f"DEBUG: Email extraction - Pattern matched: {bool(customer_email_match)}")
            if customer_email_match:
                print(f"DEBUG: Extracted email: '{customer_email_match.group(1)}'")
            else:
                print(f"DEBUG: Email pattern not found in HTML")
                # Print part of the HTML to help debug the issue
                email_snippet = html_content[html_content.find("Email"):html_content.find("Email")+200] if "Email" in html_content else "Email field not found in HTML"
                print(f"DEBUG: HTML snippet around Email: {email_snippet}")
            cleaners_required_match = re.search(r'<p><strong>Cleaners Required:</strong>\s*([^<]+)</p>', html_content)
            # Try different patterns for price since it appears differently in customer vs business emails
            price_match = re.search(r'<p><strong>Total Price:</strong>\s*<span class="price">&pound;([^<]+)</span></p>', html_content)
            if not price_match:
                # Try business email format (in table)
                price_match = re.search(r'<tr class="total-row">\s*<td>Total Price</td>\s*<td>&pound;([^<]+)</td>\s*</tr>', html_content)
            
            # Try different patterns for quote ID since it appears in different formats
            quote_id_match = re.search(r'<h2>Quote Summary \(ID: ([^<]+)\)</h2>', html_content)
            if not quote_id_match:
                quote_id_match = re.search(r'<p><strong>Quote ID:</strong>\s*([^<]+)</p>', html_content)
            if not quote_id_match:
                quote_id_match = re.search(r'<p><strong>Your reference number:</strong>\s*([^<]+)</p>', html_content)
            
            # Extract quote ID from subject line if we couldn't find it in the HTML
            subject_quote_id_match = None
            if "(ID:" in subject:
                subject_quote_id_match = re.search(r'\(ID: ([^)]+)\)', subject)
            
            # Extract quote ID if it's in the subject
            extracted_quote_id = None
            if quote_id_match:
                extracted_quote_id = quote_id_match.group(1)
            elif subject_quote_id_match:
                extracted_quote_id = subject_quote_id_match.group(1)
            
            # Print debug info for quote ID extraction
            print(f"DEBUG: Extracted quote_id: {extracted_quote_id}")
            
            # Build enhanced template parameters
            # Check if the quote ID is in the subject
            direct_quote_id = None
            if "(ID:" in subject:
                direct_quote_id_match = re.search(r'\(ID: ([^)]+)\)', subject)
                if direct_quote_id_match:
                    direct_quote_id = direct_quote_id_match.group(1)
            
            # Critical fix: Always ensure to_email is used as the recipient
            # This ensures customer emails go to customers and admin emails go to admin
            recipient_email = to_email
            
            template_params = {
                'to_email': recipient_email,  # Explicitly set recipient email
                'to_name': customer_name_match.group(1) if customer_name_match else 'Customer',
                'reply_to': config.get("company_email", "info@kmiservices.co.uk"),
                'subject': subject,
                'html_content': html_content,
                # Add extracted fields as direct parameters
                'customer_name': customer_name_match.group(1) if customer_name_match else 'Customer',
                'customer_email': customer_email_match.group(1) if customer_email_match else 'Not provided',
                'phone': direct_phone if direct_phone else (customer_phone_match.group(1) if customer_phone_match else 'Not provided'),
                'property_size': property_size_match.group(1) if property_size_match else 'Property',
                'service_type': service_type_match.group(1) if service_type_match else 'Cleaning Service',
                'cleaning_date': format_date_uk(cleaning_date_match.group(1)) if cleaning_date_match else 'To be scheduled',
                'hours_required': hours_required_match.group(1) if hours_required_match else '0',
                'cleaners_required': cleaners_required_match.group(1) if cleaners_required_match else '1',
                # Format the price to show only 2 decimal places
                # First try to extract from HTML, if it's 0.00 or not found, use a fixed value
                'total_price': (
                    "{:.2f}".format(float(price_match.group(1))) if price_match and price_match.group(1) not in ['0.00', '0'] 
                    else '0.00'
                ),
                'quote_id': extracted_quote_id if extracted_quote_id else (direct_quote_id if direct_quote_id else 'Quote'),
                # Also provide it as id directly in case the template uses a different variable name
                'id': extracted_quote_id if extracted_quote_id else (direct_quote_id if direct_quote_id else 'Quote')
            }
            
            # Log who we're sending to for debugging
            print(f"Email will be sent to: {recipient_email}")
            
            # Add debugging for price extraction
            print(f"DEBUG: Price extraction from html: {price_match.group(1) if price_match else 'Not found'}")

            # Print the template parameters for debugging
            print("EmailJS Template Parameters:")
            for key, value in template_params.items():
                if key != 'html_content':  # Skip html_content as it's too long
                    print(f"  {key}: {value}")
                    
            # Special focus on phone field for debugging
            print(f"DEBUG: Phone parameter: '{template_params.get('phone', 'NOT SET')}'")
            print(f"DEBUG: Template ID being used: {emailjs_template_id}")
            print(f"DEBUG: Email type: {email_type}")
            
            payload = {
                'service_id': emailjs_service_id,
                'template_id': emailjs_template_id,
                'user_id': emailjs_user_id,
                'accessToken': emailjs_private_key,
                'template_params': template_params
            }
            
# Make the API request to EmailJS
headers = {
    'Content-Type': 'application/json',
    'Origin': 'https://kmiservices.co.uk'  # Add origin header to bypass browser check
}
# Convert payload to JSON and handle potential string/list index errors
try:
   payload_json = json.dumps(payload)
except TypeError as e:
  if "indices must be integers or slices" in str(e):
     print(f"ERROR: List indices error detected in EmailJS payload: {str(e)}")
     # Clone the template params to fix any potential issues
     # Fix code...
     fixed_template_params = {}
     for key, value in template_params.items():
       if isinstance(value, dict) or isinstance(value, list):
          fixed_template_params[key] = str(value)
       else:
         fixed_template_params[key] = value
        
        # Create new payload with fixed parameters
        payload['template_params'] = fixed_template_params
        payload_json = json.dumps(payload)
   else:
    raise

     # Create new payload with fixed parameters

     response = requests.post(
       'https://api.emailjs.com/api/v1.0/email/send',
       data=payload_json,
       headers=headers
)
            
            print(f"EmailJS response: {response.text}")  # Debug response
            
            # Check if the email was sent successfully
            if response.status_code == 200:
                print(f"Email sent to {recipient_email} successfully via EmailJS!")
                return True
            else:
                print(f"Failed to send email via EmailJS to {recipient_email}: {response.text}")
                return False
                
        except Exception as e:
            print(f"Error sending email via EmailJS: {str(e)}")
            return False
            
    print("ERROR: No email sending method is properly configured.")
    return False

def send_customer_email(quote_data, is_scheduled=False, is_admin_sending=False):
    """Send quote email to customer"""
    from utils.database import update_sent_to_customer
    
    customer_email = quote_data["customer_info"]["email"]
    customer_name = quote_data["customer_info"]["name"]
    subject, html_content = create_customer_email_content(quote_data, is_scheduled)
    
    # Determine the email type based on context:
    # - customer_schedule: When it's a scheduling confirmation
    # - customer_quote: Initial quote request (no pricing)
    # - customer_full_quote: When admin sends the full quote with pricing
    if is_scheduled:
        email_type = "customer_schedule"
    elif is_admin_sending:
        email_type = "customer_full_quote"  # New email type for the full quote with pricing
    else:
        email_type = "customer_quote"
    
    # If this is the full quote being sent from admin, add T&C link
    if is_admin_sending:
        # Add terms and conditions section before closing tags
        tc_section = """
        <div style="margin-top: 20px; padding: 15px; background-color: #f9f9f9; border-radius: 5px;">
            <p><strong>Terms and Conditions</strong></p>
            <p>By accepting this quote, you agree to our <a href="https://kmiservices.co.uk/terms">Terms and Conditions</a>.</p>
            <p>Please review them before requesting a cleaning date.</p>
        </div>
        """
        
        # Insert the T&C section before the closing container div
        html_content = html_content.replace('</div>\n    </body>', f'{tc_section}\n        </div>\n    </body>')
    
    # Try to use SMTP directly first if available (more reliable for controlling recipient)
    import os
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    
    if os.environ.get('EMAIL_USER') and os.environ.get('EMAIL_PASSWORD'):
        try:
            print(f"Trying to send direct customer email via SMTP to {customer_email}...")
            # Get SMTP configuration from environment variables
            smtp_server = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
            smtp_port = int(os.environ.get('SMTP_PORT', 587))
            email_user = os.environ.get('EMAIL_USER')
            email_password = os.environ.get('EMAIL_PASSWORD')
            
            # Create message
            message = MIMEMultipart('alternative')
            message['Subject'] = subject
            message['From'] = email_user
            message['To'] = customer_email
            
            # Attach HTML content
            html_part = MIMEText(html_content, 'html')
            message.attach(html_part)
            
            # Connect to server and send
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            # Make sure we have string values for login
            if email_user and email_password:
                server.login(str(email_user), str(email_password))
                server.sendmail(str(email_user), customer_email, message.as_string())
            server.quit()
            
            print(f"Customer email sent directly to {customer_email} via SMTP successfully!")
            
            # Mark as sent to customer in the database
            if "quote_id" in quote_data:
                update_sent_to_customer(quote_data["quote_id"], True)
                
            return True
        except Exception as e:
            print(f"Error sending direct customer email via SMTP: {str(e)}")
            # Fall back to regular send_email
    
    # Get the customer phone if available
    customer_phone = quote_data["customer_info"].get("phone", "Not provided")
    
    # Fall back to regular EmailJS method
    success = send_email(customer_email, subject, html_content, email_type=email_type, direct_phone=customer_phone)
    
    # Mark as sent to customer in the database
    if success and "quote_id" in quote_data:
        update_sent_to_customer(quote_data["quote_id"], True)
        
    return success

def send_business_email(quote_data, is_scheduled=False, is_admin_sending=False):
    """Send detailed quote email to business"""
    config = load_config()
    business_email = config["company_email"]
    
    # Make sure we have the price correctly formatted for the business email
    if "price_details" in quote_data and "total_price" in quote_data["price_details"]:
        # Format the total price to 2 decimal places to avoid floating point issues
        raw_price = quote_data["price_details"]["total_price"]
        formatted_price = "{:.2f}".format(float(raw_price))
        quote_data["price_details"]["total_price"] = float(formatted_price)
        print(f"BUSINESS EMAIL: Fixed price formatting - Raw: {raw_price}, Formatted: {formatted_price}")
    
    subject, html_content = create_business_email_content(quote_data, is_scheduled)
    
    # Determine the email type based on context
    if is_scheduled:
        email_type = "admin_schedule"
    elif is_admin_sending:
        email_type = "admin_full_quote"  # New type for when admin sends full quote to customer
        # Update subject to reflect this is a sent quote, not just a new quote
        subject = subject.replace("New Quote", "Sent Quote")
    else:
        email_type = "admin_quote"
    
    # Print debug information for business email
    quote_id = quote_data.get("quote_id", "N/A")
    print(f"DEBUG: Sending business email for quote_id: {quote_id}")
    
    # Add quote ID to subject if not already included
    if "(ID:" not in subject and quote_id != "N/A":
        subject += f" (ID: {quote_id})"
        
    # Make sure we're explicitly sending to the business email address
    print(f"Sending business email to: {business_email}")
    
    # Modify HTML content to ensure quote ID is included
    # Add a hidden div with the quote ID that our regex can find
    if quote_id != "N/A" and "<div id='quote-id-marker'" not in html_content:
        # Insert after the opening body tag
        body_pos = html_content.find("<body>")
        if body_pos > 0:
            marker_div = f"<div id='quote-id-marker' style='display:none;'><p><strong>Quote ID:</strong> {quote_id}</p></div>"
            html_content = html_content[:body_pos+6] + marker_div + html_content[body_pos+6:]
    
    # Try to use SMTP directly first if available (more reliable for controlling recipient)
    import os
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    
    if os.environ.get('EMAIL_USER') and os.environ.get('EMAIL_PASSWORD'):
        try:
            print(f"Trying to send direct business email via SMTP to {business_email}...")
            # Get SMTP configuration from environment variables
            smtp_server = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
            smtp_port = int(os.environ.get('SMTP_PORT', 587))
            email_user = os.environ.get('EMAIL_USER')
            email_password = os.environ.get('EMAIL_PASSWORD')
            
            # Create message
            message = MIMEMultipart('alternative')
            message['Subject'] = subject
            message['From'] = email_user
            message['To'] = business_email
            
            # Attach HTML content
            html_part = MIMEText(html_content, 'html')
            message.attach(html_part)
            
            # Connect to server and send
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            # Make sure we have string values for login
            if email_user and email_password:
                server.login(str(email_user), str(email_password))
                server.sendmail(str(email_user), business_email, message.as_string())
            server.quit()
            
            print(f"Business email sent directly to {business_email} via SMTP successfully!")
            return True
        except Exception as e:
            print(f"Error sending direct business email via SMTP: {str(e)}")
            # Fall back to regular send_email
    
    # Get the customer phone if available
    customer_phone = quote_data["customer_info"].get("phone", "Not provided")
    
    # Fall back to regular EmailJS method
    return send_email(business_email, subject, html_content, email_type=email_type, direct_phone=customer_phone)
