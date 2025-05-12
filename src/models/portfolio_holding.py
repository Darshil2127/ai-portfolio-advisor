from src.main import db # Import db instance from main.py
import datetime

class PortfolioHolding(db.Model):
    __tablename__ = 'portfolio_holding'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # For simplicity in V1, we won't tie to a user account, but use a session_id
    # In a multi-user system, this would be a ForeignKey to a User table
    session_id = db.Column(db.String(255), nullable=False, index=True) 
    ticker_symbol = db.Column(db.String(20), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    purchase_price = db.Column(db.Float, nullable=True)
    purchase_date = db.Column(db.Date, nullable=True)
    uploaded_at = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)

    def __repr__(self):
        return f'<PortfolioHolding {self.ticker_symbol} ({self.quantity}) for session {self.session_id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'session_id': self.session_id,
            'ticker_symbol': self.ticker_symbol,
            'quantity': self.quantity,
            'purchase_price': self.purchase_price,
            'purchase_date': self.purchase_date.isoformat() if self.purchase_date else None,
            'uploaded_at': self.uploaded_at.isoformat()
        }

