# 🎫 License Generator Manager

A powerful Flask-based application for managing software licenses with support for tiered pricing, subscription management, and WordPress integration.

## ✨ Features

- 🔑 Generate and manage software licenses
- 📊 Admin dashboard with comprehensive analytics
- 💰 Tiered pricing (Basic, Pro, Premium)
- 📅 Monthly and yearly subscription support
- 📧 Automated email notifications
- 🔄 Real-time license validation API
- 🌐 WordPress integration support
- 📈 Detailed usage statistics
- ⏰ Expiration monitoring and alerts

## 🚀 Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/license-generator-manager.git
cd license-generator-manager
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create environment file:
```bash
cp env.txt .env
```

5. Configure your `.env` file with:
```env
SECRET_KEY=your-secret-key
ADMIN_USERNAME=your-admin-username
ADMIN_PASSWORD=your-secure-password
MAIL_SERVER=your-smtp-server
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email
MAIL_PASSWORD=your-email-password
FLASK_DEBUG=False
```

## ⚙️ Configuration

### Email Setup
Configure the email settings in `.env` to enable license key delivery:
- MAIL_SERVER: Your SMTP server (e.g., smtp.gmail.com)
- MAIL_PORT: SMTP port (typically 587 for TLS)
- MAIL_USERNAME: Your email address
- MAIL_PASSWORD: Your email password or app-specific password

### Admin Access
Set secure credentials in `.env`:
- ADMIN_USERNAME: Choose a strong username
- ADMIN_PASSWORD: Set a secure password

## 🔧 Usage

1. Start the application:
```bash
python app.py
```

2. Access the admin dashboard:
- Open http://localhost:5000 in your browser
- Log in with your admin credentials

### 📝 License Management

1. Generate License:
   - Fill in customer email
   - Select tier (Basic/Pro/Premium)
   - Choose subscription type (Monthly/Yearly)
   - System generates and emails the license key

2. Monitor Licenses:
   - View all active licenses
   - Track expiring licenses
   - Monitor usage statistics
   - Revoke licenses if needed

### 🔌 API Integration

Validate licenses via the API endpoint:
```bash
curl -X POST http://your-domain/api/validate_license \
  -H "Content-Type: application/json" \
  -d '{"license_key": "XXXX-XXXX-XXXX-XXXX-XXXX-XXXX"}'
```

## 🔒 Security Considerations

1. Always use HTTPS in production
2. Set strong admin credentials
3. Generate a secure SECRET_KEY
4. Keep .env file secure
5. Regular security updates
6. Database backups

## 💻 Development

### Project Structure
```
license_generator_manager/
├── app.py              # Main application file
├── database.py         # Database models
├── requirements.txt    # Project dependencies
├── wsgi.py            # WSGI entry point
└── templates/         # HTML templates
    ├── dashboard.html
    └── login.html
```

## 📦 Pricing Tiers

| Feature               | Basic     | Pro       | Premium   |
|----------------------|-----------|-----------|-----------|
| Monthly Price        | $4.99     | $9.99     | $24.99    |
| Yearly Price         | $49.99    | $99.99    | $249.99   |

## 🌟 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support, please open an issue in the GitHub repository or contact the maintainer.
