Setting Up Google Drive Backups for KMI Services Quote System
This guide explains how to set up automatic CSV backups to your Google Drive.

Prerequisites
Google account with access to Google Drive
Access to your KMI Services Quote System deployment
Step 1: Enable Google Drive API
Go to Google Cloud Console
Create a new project or select an existing one
Navigate to "APIs & Services" > "Library"
Search for "Google Drive API" and enable it
Step 2: Create Service Account
In Google Cloud Console, go to "APIs & Services" > "Credentials"
Click "Create Credentials" and select "Service Account"
Enter a name for the service account (e.g., "KMI-Quotes-Backup")
Grant the role "Editor" to allow file creation
Complete the setup and click "Done"
Step 3: Create and Download Service Account Key
Find your new service account in the credentials list
Click on the service account name
Go to the "Keys" tab
Click "Add Key" > "Create new key"
Select "JSON" format and click "Create"
The key file will be downloaded to your computer
Step 4: Create a Google Drive Folder for Backups
Go to your Google Drive
Create a new folder (e.g., "KMI-Quotes-Backups")
Right-click the folder and select "Share"
Add the service account email (ends with @*.gserviceaccount.com)
Set permission to "Editor"
Copy the folder ID from the URL (the long string after "folders/" in the URL)
Step 5: Add Credentials to Replit
Upload the JSON key file to your Replit project

Keep this file secure and never share it publicly
If using Git, add it to .gitignore
Add environment variables in your Replit:

GOOGLE_DRIVE_CREDENTIALS: Path to your JSON key file (e.g., "kmi-service-account.json")
GOOGLE_DRIVE_FOLDER_ID: The ID of your shared Google Drive folder
Step 6: Test the Backup System
Run the backup script manually to test:

python cron_backup.py
Check your Google Drive folder to see if the backup was created successfully.

Step 7: Schedule Regular Backups
Option 1: Using Replit's Built-in Tasks (if available)
Set up a scheduled task to run python cron_backup.py at your preferred interval.

Option 2: Using an External Scheduler
If you're hosting on a different platform:

Set up a cron job to run the backup script (examples):

Daily: 0 0 * * * /path/to/python /path/to/cron_backup.py
Weekly: 0 0 * * 0 /path/to/python /path/to/cron_backup.py
For platforms without cron:

Use scheduled GitHub actions
Use cloud scheduler services like Google Cloud Scheduler
Use external cron services like cron-job.org
Customizing the Backup Schedule
Edit the cron_backup.py file to change what gets backed up:

Change the frequency of backups
Add notifications (email, Slack, etc.) when backups complete or fail
Customize retention policy (e.g., keep only last 10 backups)
Accessing Backed-Up Data
To restore from a backup:

Download the CSV file from Google Drive
Import it into your database using the admin tools
Alternatively, you can use the CSV directly for data analysis
Troubleshooting
If backups aren't working:

Check that the service account has proper permissions on the Google Drive folder
Verify that the credentials file path is correct
Check that the Google Drive API is enabled for your project
Look for error messages in the console output
For API quota issues:

The free tier has limits on API requests
Space out your backups to avoid hitting these limits