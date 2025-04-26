KMI Services Quote System - Admin Guide
This guide explains how to use the admin features of your quote system to manage pricing, view quotes, and handle customer requests.

Accessing the Admin Area
Go to your quote system URL
Click on "Settings" in the sidebar navigation
Enter your admin password (set as ADMIN_PASSWORD in your environment variables)
You now have access to all administrative functions
Pricing Configuration
The pricing configuration controls all calculations in the quote system. Here's how to update different aspects:

Basic Pricing Settings
Go to Settings → Pricing Configuration
Adjust the following:
Hourly Rate: Base rate for your cleaning staff (default: £15)
Markup Percentage: Business markup applied to all quotes (default: 30%)
Property Size and Service Type Settings
In the Hours Required section, you can edit:

How many hours are needed for each property size and service type
Example: A 3-bedroom house with deep cleaning might need 5 hours
In the Cleaners Required section, you can specify:

How many cleaners should be assigned to each job type
Example: 1 cleaner for 1-2 bedroom properties, 2 cleaners for larger homes
Regional Pricing Adjustments
In the Region Multipliers section, you can:
Set price multipliers for different regions
Example: Central London may have a 1.3 multiplier to account for higher costs
Additional Service Pricing
In the Additional Service Costs section, adjust:

Oven cleaning costs
Carpet cleaning (per room)
Window cleaning (internal/external)
Balcony/patio cleaning
Cleaning materials provision
Click "Save Pricing Configuration" to apply all changes

Managing Quotes
The Quotes Management area allows you to review, adjust, and process customer quotes:

Viewing Quotes
Click on "View Quotes" in the sidebar
See all submitted quotes with status indicators:
Quoted: Initial quote created
Sent to Customer: Quote has been emailed to customer
Schedule Requested: Customer has accepted and requested a date
Scheduled: Cleaning has been confirmed and scheduled
Completed: Cleaning service has been performed
Cancelled: Quote was cancelled
Quote Management Actions
For each quote, you can:

View Details: See full quote information

Adjust Quote:

Apply regular client discounts
Adjust cleaner count
Modify markup percentage
Add admin notes
Send to Customer: Review and approve quotes before sending to customers

Confirm Schedule: When customers request dates, confirm with your contractors and finalize the schedule

Dashboard Analytics
The dashboard provides business insights:

Revenue Overview:

Total quoted value
Conversion rates (quotes to bookings)
Average quote value
Regional Analysis:

Bookings by region
Revenue by region
Service Popularity:

Most requested service types
Popular additional services
Customer Insights:

New vs returning customers
Referral source analysis (how customers found you)
Email Management
The system sends several types of emails:

Quote Request Notifications:

Sent to the business when customers request quotes
Contains all quote details for review
Customer Quote Emails:

Sent to customers after admin approval
Contains essential details and a link to request cleaning
Schedule Request Notifications:

Sent to business when customers request cleaning dates
Contains customer preferences and requirements
Schedule Confirmation Emails:

Sent to customers after admin confirms cleaning dates
Contains final confirmation and preparation instructions
To modify email templates:

Edit appropriate sections in utils/email_service.py
Update matching EmailJS templates (if using EmailJS)
System Maintenance
Database Management
The system uses both PostgreSQL and CSV storage:

Database Backup:

Periodically backup your database using pg_dump
Store backups in a secure location
CSV Export:

Download the CSV files regularly as a secondary backup
Located in the data folder
Clearing Old Data
For GDPR compliance and system performance:

Create a data retention policy (e.g., delete quotes older than 2 years)
Regularly review and clean up old data
Ensure backups are kept before deletion
Security Recommendations
Admin Password:

Change your admin password regularly
Use a strong, unique password
Store it in a password manager
Environment Variables:

Keep all sensitive information in environment variables
Never hardcode credentials in the application
Access Control:

Limit admin access to necessary personnel only
Consider implementing more granular user roles if needed
Getting Help
If you encounter issues or need assistance:

Check the console logs for error messages
Review the deployment guide for configuration issues
Reach out to technical support for complex problems