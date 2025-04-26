Setting Up EmailJS for KMI Services Quote System
This guide provides step-by-step instructions for integrating EmailJS with your KMI Services Quote System.

What You'll Need
An EmailJS account (free tier available at EmailJS.com)
Access to your Replit environment variables
Basic HTML/email template knowledge
Step 1: Create an EmailJS Account
Go to EmailJS.com and sign up for an account
Verify your email address
Step 2: Configure Email Service
In the EmailJS dashboard, click "Add New Service"
Select your email provider (Gmail, Outlook, custom SMTP, etc.)
Configure and authenticate your email service
Name your service "KMI-Quotes" or something similar
Copy the Service ID for later use
Step 3: Create Email Templates
You'll need to create 6 different templates for the different email types:

Template 1: Customer Quote Request Confirmation
Click "Create New Template"
Name it "customer-quote-request"
Use this template structure:
<h1>Thank You For Your Quote Request</h1>
<p>Dear {{customer_name}},</p>
<p>Thank you for requesting a quote from {{company_name}}. We have received your request and our team is reviewing your requirements.</p>
<p><strong>Your reference number:</strong> {{quote_id}}</p>
<p>We'll be in touch shortly with your customized quote.</p>
<p>Thank you for considering {{company_name}}!</p>
<p>Best regards,<br>The {{company_name}} Team</p>
Template 2: Admin Quote Notification
Click "Create New Template"
Name it "admin-quote-notification"
Use this template structure:
<h1>New Quote Request</h1>
<p><strong>Quote ID:</strong> {{quote_id}}</p>
<p><strong>Customer:</strong> {{customer_name}}</p>
<p><strong>Email:</strong> {{customer_email}}</p>
<p><strong>Phone:</strong> {{phone}}</p>
<p><strong>Property Size:</strong> {{property_size}}</p>
<p><strong>Service Type:</strong> {{service_type}}</p>
<p><strong>Total Price:</strong> £{{total_price}}</p>
<p>Please review this quote in the admin panel before sending to the customer.</p>
Template 3: Customer Schedule Request Confirmation
Click "Create New Template"
Name it "customer-schedule-request"
Use this template structure:
<h1>Thank You For Your Cleaning Date Request</h1>
<p>Dear {{customer_name}},</p>
<p>Thank you for accepting our quote and requesting a cleaning date. We have received your preferred date and time:</p>
<p><strong>Date:</strong> {{cleaning_date}}<br>
<strong>Time:</strong> {{time_preference}}</p>
<p>Our team will check contractor availability and contact you shortly to confirm your booking.</p>
<p>By proceeding with this booking, you agree to our <a href="https://kmiservices.co.uk/terms">Terms and Conditions</a>.</p>
<p>Thank you for choosing {{company_name}}!</p>
<p>Best regards,<br>The {{company_name}} Team</p>
Template 4: Admin Schedule Notification
Click "Create New Template"
Name it "admin-schedule-notification"
Use this template structure:
<h1>New Cleaning Schedule Request</h1>
<p><strong>Quote ID:</strong> {{quote_id}}</p>
<p><strong>Customer:</strong> {{customer_name}}</p>
<p><strong>Email:</strong> {{customer_email}}</p>
<p><strong>Phone:</strong> {{phone}}</p>
<p><strong>Address:</strong> {{customer_address}}</p>
<p><strong>Date Requested:</strong> {{cleaning_date}}</p>
<p><strong>Time Preference:</strong> {{time_preference}}</p>
<p><strong>Service:</strong> {{service_type}} cleaning for {{property_size}} property</p>
<p><strong>Estimated Hours:</strong> {{hours_required}}</p>
<p><strong>Cleaners Required:</strong> {{cleaners_required}}</p>
<p>Please check contractor availability and confirm this booking with the customer.</p>
Template 5: Customer Full Quote (With Pricing)
Click "Create New Template"
Name it "customer-full-quote"
Use this template structure:
<h1>Your Cleaning Quote from KMI Services</h1>
<p>Dear {{customer_name}},</p>
<p>Thank you for your enquiry with KMI Services. We're pleased to provide your customized cleaning quote:</p>
<div style="background-color: #f9f9f9; padding: 15px; border-radius: 5px; margin-bottom: 20px;">
    <h2>Quote Summary (ID: {{quote_id}})</h2>
    <p><strong>Service Type:</strong> {{service_type}}</p>
    <p><strong>Property Size:</strong> {{property_size}}</p>
    <p><strong>Time Required:</strong> {{hours_required}} hours</p>
    <p><strong>Cleaners Required:</strong> {{cleaners_required}}</p>
    <p><strong>Total Price:</strong> <span style="font-size: 24px; font-weight: bold; color: #22C7D6;">&pound;{{total_price}}</span></p>
</div>
<p>This quote is valid for 30 days.</p>
<div style="text-align: center; margin: 20px 0;">
    <a href="https://kmiservices.co.uk/schedule?quote_id={{quote_id}}" style="display: inline-block; background-color: #22C7D6; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; font-weight: bold; font-size: 16px;">Request Cleaning Date</a>
</div>
<p>By accepting this quote, you agree to our <a href="https://kmiservices.co.uk/terms">Terms and Conditions</a>.</p>
<p>Thank you for choosing KMI Services!</p>
<p>Best regards,<br>The KMI Services Team</p>
Template 6: Admin Full Quote Notification
Click "Create New Template"
Name it "admin-full-quote-notification"
Use this template structure:
<h1>Quote Sent to Customer</h1>
<p><strong>Quote ID:</strong> {{quote_id}}</p>
<p><strong>Customer:</strong> {{customer_name}}</p>
<p><strong>Email:</strong> {{customer_email}}</p>
<p><strong>Phone:</strong> {{phone}}</p>
<p><strong>Property Size:</strong> {{property_size}}</p>
<p><strong>Service Type:</strong> {{service_type}}</p>
<p><strong>Total Price:</strong> &pound;{{total_price}}</p>
<p>This quote has been sent to the customer with full pricing details.</p>
Step 4: Get Your EmailJS Credentials
Go to "Account" > "API Keys" in the EmailJS dashboard
Copy your User ID
Note down all Template IDs you created above
Note your Service ID from Step 2
Step 5: Configure Environment Variables in Replit
Go to your Replit project
Click on the "Secrets" tool (lock icon) in the sidebar
Add the following environment variables:
Key: EMAILJS_USER_ID | Value: [Your User ID]
Key: EMAILJS_SERVICE_ID | Value: [Your Service ID]
Key: EMAILJS_CUSTOMER_QUOTE_TEMPLATE_ID | Value: [Template ID for customer-quote-request]
Key: EMAILJS_ADMIN_QUOTE_TEMPLATE_ID | Value: [Template ID for admin-quote-notification]
Key: EMAILJS_CUSTOMER_SCHEDULE_TEMPLATE_ID | Value: [Template ID for customer-schedule-request]
Key: EMAILJS_ADMIN_SCHEDULE_TEMPLATE_ID | Value: [Template ID for admin-schedule-notification]
Key: EMAILJS_CUSTOMER_FULL_QUOTE_TEMPLATE_ID | Value: [Template ID for customer-full-quote]
Key: EMAILJS_ADMIN_FULL_QUOTE_TEMPLATE_ID | Value: [Template ID for admin-full-quote-notification]
Step 6: Update the Email Service Code
The app is already configured to use EmailJS, but you may need to adjust the code for your specific template IDs. If you used different template names, edit utils/email_service.py to match your template IDs.

Step 7: Test EmailJS Integration
Open your app and submit a test quote
Check if the emails are delivered to both customer and admin addresses
Test the scheduling feature to ensure those emails are sent correctly
Troubleshooting
Emails Not Sending:

Check the Replit console logs for errors
Verify your EmailJS credentials are correctly set in environment variables
Make sure your templates have all the required variables
Confirm your monthly email quota hasn't been exceeded (free tier limits apply)
Template Variables Not Working:

Ensure variable names in your templates match the data sent from the app
Check for typos in variable names
Use the EmailJS testing feature to test templates directly
Rate Limits:

Free accounts have sending limits
Consider upgrading if you need to send more emails
Email Best Practices
Include your business logo in the email templates
Add a clear call-to-action button
Keep emails mobile-friendly
Include your contact information
Add unsubscribe options as required by regulations