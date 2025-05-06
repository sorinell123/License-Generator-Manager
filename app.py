from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_mail import Mail, Message
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from database import db, License, init_db
import os
from datetime import datetime, timedelta
import secrets
import string
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app, resources={
    "/api/*": {
        "origins": "*",
        "methods": ["POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///licenses.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Mail settings
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True') == 'True'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')

mail = Mail(app)
init_db(app)

# User model for admin login
class User(UserMixin):
    def __init__(self, user_id, username):
        self.id = user_id
        self.username = username

# Admin user credentials
ADMIN_USER = User(1, os.getenv('ADMIN_USERNAME', 'admin'))
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'admin')

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    if int(user_id) == 1:
        return ADMIN_USER
    return None

def generate_license_key():
    # Generate a 24-character key in format XXXX-XXXX-XXXX-XXXX-XXXX-XXXX
    chars = string.ascii_uppercase + string.digits
    segments = [''.join(secrets.choice(chars) for _ in range(4)) for _ in range(6)]
    return '-'.join(segments)

@app.route('/')
@login_required
def dashboard():
    licenses = License.query.all()
    stats = License.get_stats()
    monthly_stats = License.get_monthly_stats()
    
    return render_template('dashboard.html', 
                         licenses=licenses,
                         stats=stats,
                         monthly_stats=monthly_stats)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if (request.form['username'] == ADMIN_USER.username and 
            request.form['password'] == ADMIN_PASSWORD):
            login_user(ADMIN_USER)
            return redirect(url_for('dashboard'))
        flash('Invalid credentials')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/generate_license', methods=['POST'])
@login_required
def generate_license():
    email = request.form.get('email')
    tier = request.form.get('tier')
    subscription_type = request.form.get('subscription_type')

    if not all([email, tier, subscription_type]):
        flash('Email, tier, and subscription type are required')
        return redirect(url_for('dashboard'))

    if tier not in ['basic', 'pro', 'premium']:
        flash('Invalid tier selected')
        return redirect(url_for('dashboard'))

    if subscription_type not in ['monthly', 'yearly']:
        flash('Invalid subscription type selected')
        return redirect(url_for('dashboard'))

    license_key = generate_license_key()
    days = 30 if subscription_type == 'monthly' else 365
    expires_at = datetime.utcnow() + timedelta(days=days)
    price = License.PRICING[tier][subscription_type]

    new_license = License(
        license_key=license_key,
        email=email,
        tier=tier,
        subscription_type=subscription_type,
        price=price,
        expires_at=expires_at
    )
    
    db.session.add(new_license)
    db.session.commit()
    
    # Send email
    try:
        msg = Message('Your License Key',
                    sender=app.config['MAIL_USERNAME'],
                    recipients=[email])
        msg.body = f'''Your license key for SMS Gateway:
{license_key}

License Details:
- Tier: {tier.capitalize()}
- Subscription: {subscription_type.capitalize()}
- Price: ${price}
- Valid until: {expires_at.strftime('%Y-%m-%d')}

Thank you for your purchase! Your license will expire on {expires_at.strftime('%Y-%m-%d')}.
To renew your license before expiration, please visit our website.'''
        mail.send(msg)
        flash('License generated and sent successfully')
    except Exception as e:
        flash(f'License generated but email failed to send: {str(e)}')
    
    return redirect(url_for('dashboard'))

import requests

@app.route('/api/validate_license', methods=['POST'])
def validate_license():
    data = request.get_json()
    if not data or 'license_key' not in data:
        return jsonify({'error': 'No license key provided'}), 400
    
    license = License.query.filter_by(license_key=data['license_key']).first()

    # Update site URL if provided
    if license and 'site_url' in data:
        license.site_url = data['site_url']
        db.session.commit()
    if not license:
        return jsonify({'error': 'Invalid license key'}), 404
    
    # Check expiration first
    if license.expires_at and license.expires_at < datetime.utcnow():
        license.status = 'expired'
        db.session.commit()
        return jsonify({'error': 'License has expired'}), 403
    
    # Then check status
    if license.status == 'revoked':
        return jsonify({'error': 'License has been revoked'}), 403
    elif license.status == 'expired':
        return jsonify({'error': 'License has expired'}), 403
    elif license.status != 'active':
        return jsonify({'error': f'License is not active (Status: {license.status})'}), 403
    
    return jsonify({'valid': True, 'license': license.to_dict()})

@app.route('/delete_license/<int:license_id>', methods=['POST'])
@login_required
def delete_license(license_id):
    license = License.query.get_or_404(license_id)
    db.session.delete(license)
    db.session.commit()
    flash('License deleted successfully')
    return redirect(url_for('dashboard'))

def notify_wordpress_site(site_url, license_key):
    try:
        requests.post(f"{site_url}/wp-json/wp-sms-gateway/v1/license-check", 
            json={"license_key": license_key},
            timeout=5
        )
    except:
        pass  # Silent fail if WordPress site unreachable

@app.route('/revoke_license/<int:license_id>', methods=['POST'])
@login_required
def revoke_license(license_id):
    license = License.query.get_or_404(license_id)
    license.status = 'revoked'
    db.session.commit()
    
    # Notify WordPress site if URL exists
    if license.site_url:
        notify_wordpress_site(license.site_url, license.license_key)
    
    flash('License revoked successfully')
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(host='0.0.0.0', debug=debug_mode)
