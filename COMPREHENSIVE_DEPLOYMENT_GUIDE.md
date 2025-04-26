Comprehensive Deployment Guide for KMI Services Application
This guide outlines the steps to deploy your Streamlit application to various platforms.

Option 1: Streamlit Community Cloud (Easiest)
Sign up for Streamlit Cloud:

Visit https://streamlit.io/cloud
Create an account or sign in with GitHub
Connect your GitHub repository:

Create a new GitHub repository
Push your code to this repository
Make sure your repository includes:
app.py
requirements.txt (use the deployment-requirements.txt we created)
All necessary folders (utils, pages, etc.)
Deploy on Streamlit Cloud:

Click "New app" in the Streamlit dashboard
Select your repository, branch, and main file (app.py)
Add your secrets (DATABASE_URL and EmailJS credentials)
Click "Deploy"
Custom domain setup (optional):

In your Streamlit app settings, you can configure a custom domain
Follow the Streamlit documentation for DNS configuration
Option 2: Vercel Deployment
Prepare for Vercel:
Create a GitHub repository with your code
Add a vercel.json file to the root of your repository:
{
    "builds": [
        {
            "src": "app.py",
            "use": "@streamlit/vercel-plugin"
        }
    ],
    "routes": [
        {
            "src": "/(.*)",
            "dest": "app.py"
        }
    ]
}
Sign up for Vercel:

Go to https://vercel.com
Sign up or log in with GitHub
Import your repository:

Click "Import Project" in Vercel
Select your GitHub repository
Configure your Environment Variables (DATABASE_URL and EmailJS credentials)
Click "Deploy"
Custom domain setup:

In your Vercel project settings, go to "Domains"
Add your custom domain and follow the DNS configuration instructions
Option 3: Self-Hosting on VPS (Advanced)
Set up a VPS (DigitalOcean, AWS EC2, Linode, etc.)

Choose a provider and create a server (Ubuntu recommended)
Set up SSH access
Install dependencies:

sudo apt update
sudo apt install python3-pip python3-dev build-essential libssl-dev libffi-dev python3-setuptools
sudo apt install python3-venv nginx
Clone your repository:
git clone https://github.com/yourusername/your-repo.git
cd your-repo
Set up Python environment:
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
Create a systemd service: Create a file at /etc/systemd/system/streamlit.service:
[Unit]
Description=Streamlit web application
After=network.target
[Service]
User=your_user
WorkingDirectory=/path/to/your/app
ExecStart=/path/to/your/app/venv/bin/streamlit run app.py --server.port=8501
Restart=always
Environment="DATABASE_URL=your_database_url"
Environment="EMAILJS_SERVICE_ID=your_emailjs_service_id"
# Add all your required environment variables here
[Install]
WantedBy=multi-user.target
Start the service:
sudo systemctl start streamlit
sudo systemctl enable streamlit
Configure Nginx: Create a file at /etc/nginx/sites-available/streamlit:
server {
    listen 80;
    server_name your_domain.com www.your_domain.com;
    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Host $host;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_read_timeout 86400;
    }
}
Enable the site and set up SSL:
sudo ln -s /etc/nginx/sites-available/streamlit /etc/nginx/sites-enabled
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your_domain.com -d www.your_domain.com
sudo systemctl restart nginx
Database Options
Option 1: Railway PostgreSQL (Recommended)
Sign up at railway.app
Create a new PostgreSQL project
Get the connection string and add it as DATABASE_URL in your deployment environment
Option 2: Supabase
Sign up at supabase.com
Create a new project
Use the PostgreSQL connection string in your deployment
Option 3: AWS RDS or DigitalOcean Managed Database
For production environments with higher requirements

Important Deployment Steps for Any Platform
Database Migration: Your initial database setup will happen automatically when you first run the application with a new database.

Environment Variables/Secrets: Make sure to set these in your deployment platform:

DATABASE_URL
EMAILJS_USER_ID
EMAILJS_SERVICE_ID
EMAILJS_TEMPLATE_ID
EMAILJS_ADMIN_TEMPLATE_ID
EMAILJS_ADMIN_FULL_QUOTE_TEMPLATE_ID
Testing Post-Deployment:

Test the quote form submission
Test admin access (password: admin123)
Test data export (CSV downloads)
Test email sending
Backup & Maintenance
Scheduled Backups:

Set up a cron job on your deployment platform to run cron_backup.py
Make sure to configure Google Drive credentials as described in GOOGLE_DRIVE_BACKUP_SETUP.md
Updates:

To update the application, push changes to your GitHub repository
Most platforms will automatically redeploy
Monitoring:

Consider adding a monitoring service like UptimeRobot or StatusCake to ensure your application stays online
Support & Troubleshooting
If you encounter any issues during deployment, refer to the specific platform's documentation:

Streamlit Cloud Docs
Vercel Documentation
DigitalOcean Tutorials
For application-specific issues, refer to the documentation in the repository:

ADMIN_GUIDE.md
EMAILJS_SETUP_GUIDE.md
GOOGLE_DRIVE_BACKUP_SETUP.md
