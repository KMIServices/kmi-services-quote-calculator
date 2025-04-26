"""
Scheduled Google Drive Backup Script

This script should be run using a scheduler like cron.
Example cron setup to run daily at midnight:
0 0 * * * /path/to/python /path/to/cron_backup.py
"""

import time
import datetime
from utils.backup_to_drive import export_db_to_csv, backup_csv_to_drive

def main():
    print(f"Starting scheduled backup at {datetime.datetime.now()}")
    
    # Export database to CSV
    export_result = export_db_to_csv()
    
    if export_result:
        print("Database exported to CSV successfully")
        
        # Backup CSV files to Google Drive
        backup_result = backup_csv_to_drive()
        
        if backup_result:
            print("CSV files backed up to Google Drive successfully")
        else:
            print("Failed to backup CSV files to Google Drive")
    else:
        print("Failed to export database to CSV")
    
    print(f"Backup process completed at {datetime.datetime.now()}")
    
if __name__ == "__main__":
    main()