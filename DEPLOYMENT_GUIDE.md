KMI Services Quote System Deployment Guide
This guide provides instructions for deploying the KMI Services Quote System on your website and managing the database and settings.

Deployment Options
Option 1: Embed in Existing Website
Add this iframe to your website where you want the quote calculator to appear:

<iframe src="https://your-replit-app-url.replit.app" width="100%" height="800px" frameborder="0"></iframe>
Customize as needed:

Adjust width/height based on your page layout
Add CSS styling to match your website theme
Consider mobile responsiveness (use percentages for width)
Option 2: Standalone Tool with Link
Deploy the Streamlit app using Replit's "Deploy" button
Add a prominent button on your main website:
<a href="https://your-replit-app-url.replit.app" class="quote-button">Get a Quote</a>
Style the button to match your website design and make it stand out.

Setting Up EmailJS Integration
Create an account at EmailJS if you don't have one

Create email templates in EmailJS for:

Customer quote requests
Admin quote notifications
Schedule confirmations
Admin schedule notifications
Get your EmailJS credentials:

User ID
Service ID
Template IDs for each template type
Add these environment variables to your Replit:

EMAILJS_USER_ID
EMAILJS_SERVICE_ID
EMAILJS_TEMPLATE_ID
Database Hosting Options
PostgreSQL Database
ElephantSQL (Recommended):

Create a free account at ElephantSQL
Create a new instance (free tier offers 20MB)
Copy the connection URL
Add it as DATABASE_URL in your Replit environment variables
Railway.app:

Sign up at Railway.app
Create a new PostgreSQL database
Copy the connection URL
Add it as DATABASE_URL in your Replit environment variables
CSV Backup Storage
For additional safety, configure automated backups:

Local Storage (default):

CSV files are stored in the /data folder by default
Download these periodically as backup
Cloud Storage Options:

Google Drive: Use the Google Drive API for automated backups
Dropbox: Use the Dropbox API
AWS S3: Use boto3 library to upload backups
Admin Access
Securing the Admin Panel
Set a secure admin password:

Add an environment variable to your Replit named ADMIN_PASSWORD
Use a strong, unique password
Access the admin panel:

Go to /settings on your deployed app
Enter your admin password
You'll now have access to all configuration options
Pricing Configuration
In the admin panel, you can adjust:

Basic pricing:

Hourly rates
Markup percentages
Time requirements:

Hours needed for each property size and service type
Number of cleaners required
Region pricing:

Set multipliers for different regions
Additional services:

Oven cleaning costs
Carpet cleaning costs
Window cleaning costs
Materials costs
All changes are saved to the configuration files automatically.

Maintenance Tasks
Regular Backups
Schedule regular database backups:

pg_dump $DATABASE_URL > backup_$(date +%Y%m%d).sql
Export CSV data periodically:

Download the data/quotes.csv file
Store in a secure location
Updating Email Templates
Modify the templates in utils/email_service.py as needed
Update corresponding templates in EmailJS
Troubleshooting
If emails aren't sending:

Check EmailJS credentials in environment variables
Verify template parameters match the data being sent
Check the console logs for error messages
If database connections fail:

Verify the DATABASE_URL is correct
Check that your database provider is online
Look for connection errors in the Replit logs
Need Help?
Contact us for technical support or custom modifications.

