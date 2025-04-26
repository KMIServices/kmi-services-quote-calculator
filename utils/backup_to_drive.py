"""
CSV Export to Google Drive

This script exports quotes data to Google Drive for backup purposes.
To set up:
1. Enable the Google Drive API in Google Cloud Console
2. Create a service account and download credentials as JSON
3. Share a Google Drive folder with the service account email
4. Add your credentials file path to DRIVE_CREDENTIALS_PATH in this file
5. Schedule this script to run regularly
"""

import os
import time
from datetime import datetime
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2 import service_account

# Configuration
DATA_DIR = os.path.join("data")
DRIVE_CREDENTIALS_PATH = os.environ.get("GOOGLE_DRIVE_CREDENTIALS", "credentials.json")
DRIVE_FOLDER_ID = os.environ.get("GOOGLE_DRIVE_FOLDER_ID", "")  # The shared Google Drive folder ID

def authenticate_drive():
    """Authenticate with Google Drive API using service account"""
    try:
        # Check if credentials file exists
        if not os.path.exists(DRIVE_CREDENTIALS_PATH):
            print(f"Error: Google Drive credentials file not found at {DRIVE_CREDENTIALS_PATH}")
            return None
            
        # Set up credentials and build service
        SCOPES = ['https://www.googleapis.com/auth/drive.file']
        credentials = service_account.Credentials.from_service_account_file(
            DRIVE_CREDENTIALS_PATH, scopes=SCOPES)
        
        service = build('drive', 'v3', credentials=credentials)
        return service
    except Exception as e:
        print(f"Authentication error: {str(e)}")
        return None

def backup_csv_to_drive():
    """Backup CSV files to Google Drive"""
    service = authenticate_drive()
    if not service:
        return False
        
    # Check if data directory exists
    if not os.path.exists(DATA_DIR):
        print(f"Error: Data directory not found at {DATA_DIR}")
        return False
        
    # Get list of CSV files in data directory
    csv_files = [f for f in os.listdir(DATA_DIR) if f.endswith('.csv')]
    if not csv_files:
        print("No CSV files found to backup")
        return False
    
    successful_backups = 0
    
    # Upload each CSV file
    for csv_file in csv_files:
        file_path = os.path.join(DATA_DIR, csv_file)
        try:
            # Add timestamp to filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_name = f"{os.path.splitext(csv_file)[0]}_{timestamp}.csv"
            
            # Create file metadata
            file_metadata = {
                'name': file_name,
                'parents': [DRIVE_FOLDER_ID]  # Optional: Place in specific folder
            }
            
            # Create media
            media = MediaFileUpload(file_path, mimetype='text/csv')
            
            # Upload file
            file = service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()
            
            print(f"Successfully backed up {csv_file} to Google Drive with ID: {file.get('id')}")
            successful_backups += 1
            
        except Exception as e:
            print(f"Error backing up {csv_file}: {str(e)}")
    
    return successful_backups > 0

def export_db_to_csv():
    """Export database data to CSV files"""
    try:
        from utils.database import get_quotes_from_db
        import pandas as pd
        
        # Create data directory if it doesn't exist
        os.makedirs(DATA_DIR, exist_ok=True)
        
        # Get quotes from database
        df = get_quotes_from_db()
        
        # Save to CSV with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_path = os.path.join(DATA_DIR, f"quotes_export_{timestamp}.csv")
        df.to_csv(csv_path, index=False)
        
        print(f"Successfully exported database to {csv_path}")
        return csv_path
    except Exception as e:
        print(f"Error exporting database to CSV: {str(e)}")
        return None

if __name__ == "__main__":
    # Export database to CSV
    export_db_to_csv()
    
    # Backup CSV to Google Drive
    result = backup_csv_to_drive()
    if result:
        print("Backup completed successfully")
    else:
        print("Backup failed or no files to backup")