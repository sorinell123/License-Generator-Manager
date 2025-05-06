# Deploying to PythonAnywhere

Follow these steps to deploy the license manager on PythonAnywhere:

1. Create a PythonAnywhere Account
   - Go to www.pythonanywhere.com and sign up for an account
   - Choose a plan that suits your needs (even the free tier works)

2. Upload Files
   - Go to the Files tab in PythonAnywhere
   - Create a new directory (e.g., `license_manager`)
   - Upload the following files/directories:
     - `app.py`
     - `wsgi.py`
     - `database.py`
     - `requirements.txt`
     - `templates/` directory
     - `.env.production` (rename to `.env` after uploading)

3. Set Up Virtual Environment
   ```bash
   # In PythonAnywhere bash console:
   cd license_manager
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

4. Configure Environment
   - Rename `.env.production` to `.env`
   - Edit `.env` and set your production values:
     - Generate a secure SECRET_KEY
     - Set strong ADMIN_USERNAME and ADMIN_PASSWORD
     - Configure your email settings

5. Set Up the Web App
   - Go to the Web tab in PythonAnywhere
   - Click "Add a new web app"
   - Choose your Python version (3.8 or later)
   - Choose "Manual Configuration"
   - Set the following:
     - Source code: /home/yourusername/license_manager
     - Working directory: /home/yourusername/license_manager
     - WSGI configuration file: Update with the path to wsgi.py

6. Configure WSGI File
   - In the Web tab, click on the WSGI configuration file link
   - Replace the contents with:
     ```python
     import sys
     import os
     from dotenv import load_dotenv

     # Add your project directory to Python path
     path = '/home/yourusername/license_manager'
     if path not in sys.path:
         sys.path.append(path)

     # Load environment variables
     load_dotenv(os.path.join(path, '.env'))

     # Import your app
     from app import app as application
     ```

7. Initialize Database
   ```bash
   # In PythonAnywhere bash console:
   cd license_manager
   source venv/bin/activate
   python
   >>> from app import db
   >>> db.create_all()
   >>> exit()
   ```

8. Update WordPress Plugin
   - Update the license validation URL in your WordPress plugin to point to:
   `https://yourusername.pythonanywhere.com/api/validate_license`

9. Reload Web App
   - Go back to the Web tab
   - Click the green "Reload" button

Your license manager should now be running on PythonAnywhere at:
`https://yourusername.pythonanywhere.com`

## Security Considerations

1. Always use HTTPS in production
2. Set strong admin credentials
3. Generate a secure secret key
4. Keep your .env file secure and never commit it to version control
5. Regularly update dependencies
6. Back up your database regularly

## Troubleshooting

1. Check the error logs in the Web tab
2. Ensure all environment variables are set correctly
3. Verify the database path and permissions
4. Check the server error logs for detailed information

## Maintenance

1. Regular updates:
   ```bash
   pip install --upgrade -r requirements.txt
   ```

2. Database backup:
   ```bash
   cp instance/licenses.db instance/licenses.db.backup
   ```

3. Monitor disk usage in PythonAnywhere dashboard
