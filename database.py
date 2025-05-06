from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class License(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    license_key = db.Column(db.String(30), unique=True, nullable=False)
    email = db.Column(db.String(120), nullable=False)
    site_url = db.Column(db.String(255), nullable=True)
    tier = db.Column(db.String(10), nullable=False)  # basic, pro, premium
    subscription_type = db.Column(db.String(10), nullable=False)  # monthly, yearly
    price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='active')  # active, expired, revoked
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=True)

    PRICING = {
        'basic': {'monthly': 4.99, 'yearly': 49.99},
        'pro': {'monthly': 9.99, 'yearly': 99.99},
        'premium': {'monthly': 24.99, 'yearly': 249.99}
    }

    def to_dict(self):
        return {
            'id': self.id,
            'license_key': self.license_key,
            'email': self.email,
            'tier': self.tier,
            'subscription_type': self.subscription_type,
            'price': self.price,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'expires_at': self.expires_at.isoformat() if self.expires_at else None
        }

    @staticmethod
    def get_stats():
        from datetime import datetime, timedelta
        now = datetime.utcnow()
        expiring_soon = now + timedelta(days=30)
        
        total = License.query.count()
        active = License.query.filter_by(status='active').count()
        revoked = License.query.filter_by(status='revoked').count()
        expired = License.query.filter_by(status='expired').count()
        expiring = License.query.filter(
            License.status == 'active',
            License.expires_at <= expiring_soon,
            License.expires_at > now
        ).count()
        
        return {
            'total': total,
            'active': active,
            'revoked': revoked,
            'expired': expired,
            'expiring_soon': expiring
        }

    @staticmethod
    def get_monthly_stats():
        from sqlalchemy import func
        from datetime import datetime, timedelta
        
        # Get the last 12 months
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=365)
        
        # Query monthly creation counts
        monthly_created = db.session.query(
            func.strftime('%Y-%m', License.created_at).label('month'),
            func.count(License.id).label('count')
        ).filter(
            License.created_at >= start_date
        ).group_by(
            func.strftime('%Y-%m', License.created_at)
        ).all()
        
        return {
            'labels': [item[0] for item in monthly_created],
            'counts': [item[1] for item in monthly_created]
        }

def init_db(app):
    db.init_app(app)
    
    with app.app_context():
        db.create_all()
