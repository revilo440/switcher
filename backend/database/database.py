"""
Database configuration and initialization
"""
from sqlalchemy import create_engine, Column, String, Float, Integer, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from datetime import datetime
import json
import os
import logging

logger = logging.getLogger(__name__)

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./payment_optimizer.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database Models
class Card(Base):
    __tablename__ = "cards"
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    issuer = Column(String, nullable=False)
    annual_fee = Column(Integer, default=0)
    reward_structure = Column(Text, nullable=False)  # JSON string
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    transactions = relationship("Transaction", back_populates="recommended_card")

class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    merchant = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    category = Column(String, nullable=False)
    recommended_card_id = Column(String, ForeignKey("cards.id"))
    actual_card_id = Column(String)
    reward_earned = Column(Float)
    date = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    recommended_card = relationship("Card", back_populates="transactions")

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")

def seed_demo_data():
    """Seed database with demo credit cards"""
    db = SessionLocal()
    try:
        # Check if data already exists
        if db.query(Card).count() > 0:
            logger.info("Database already seeded")
            return
        
        # Demo cards with realistic reward structures
        demo_cards = [
            {
                "id": "chase-sapphire-preferred",
                "name": "Chase Sapphire Preferred",
                "issuer": "Chase",
                "annual_fee": 95,
                "reward_structure": json.dumps({
                    "default_rate": 1.0,
                    "categories": {
                        "dining": 3.0,
                        "travel": 2.0,
                        "streaming": 3.0,
                        "online_grocery": 3.0
                    },
                    "reward_type": "points",
                    "point_value": 0.015,
                    "signup_bonus": "60,000 points after $4k spend"
                })
            },
            {
                "id": "amex-blue-cash-preferred",
                "name": "American Express Blue Cash Preferred",
                "issuer": "American Express",
                "annual_fee": 95,
                "reward_structure": json.dumps({
                    "default_rate": 1.0,
                    "categories": {
                        "grocery": 6.0,
                        "streaming": 6.0,
                        "gas": 3.0,
                        "transit": 3.0
                    },
                    "reward_type": "cashback",
                    "annual_caps": {
                        "grocery": 6000
                    },
                    "signup_bonus": "$350 after $3k spend"
                })
            },
            {
                "id": "citi-double-cash",
                "name": "Citi Double Cash",
                "issuer": "Citi",
                "annual_fee": 0,
                "reward_structure": json.dumps({
                    "default_rate": 2.0,
                    "categories": {},
                    "reward_type": "cashback",
                    "signup_bonus": "$200 after $1.5k spend"
                })
            },
            {
                "id": "capital-one-savor",
                "name": "Capital One Savor",
                "issuer": "Capital One",
                "annual_fee": 95,
                "reward_structure": json.dumps({
                    "default_rate": 1.0,
                    "categories": {
                        "dining": 4.0,
                        "entertainment": 4.0,
                        "grocery": 3.0,
                        "streaming": 3.0
                    },
                    "reward_type": "cashback",
                    "signup_bonus": "$300 after $3k spend"
                })
            },
            {
                "id": "chase-freedom-unlimited",
                "name": "Chase Freedom Unlimited",
                "issuer": "Chase",
                "annual_fee": 0,
                "reward_structure": json.dumps({
                    "default_rate": 1.5,
                    "categories": {
                        "dining": 3.0,
                        "drugstore": 3.0,
                        "travel_chase": 5.0
                    },
                    "reward_type": "cashback",
                    "signup_bonus": "$200 after $500 spend"
                })
            },
            {
                "id": "amex-gold",
                "name": "American Express Gold Card",
                "issuer": "American Express",
                "annual_fee": 250,
                "reward_structure": json.dumps({
                    "default_rate": 1.0,
                    "categories": {
                        "dining": 4.0,
                        "grocery": 4.0,
                        "flights": 3.0
                    },
                    "reward_type": "points",
                    "point_value": 0.02,
                    "annual_caps": {
                        "grocery": 25000
                    },
                    "signup_bonus": "90,000 points after $6k spend"
                })
            }
        ]
        
        # Insert demo cards
        for card_data in demo_cards:
            card = Card(**card_data)
            db.add(card)
        
        # Add some demo transactions
        demo_transactions = [
            {
                "merchant": "Starbucks",
                "amount": 5.50,
                "category": "dining",
                "recommended_card_id": "capital-one-savor",
                "reward_earned": 0.22
            },
            {
                "merchant": "Whole Foods",
                "amount": 120.00,
                "category": "grocery",
                "recommended_card_id": "amex-blue-cash-preferred",
                "reward_earned": 7.20
            },
            {
                "merchant": "Shell Gas Station",
                "amount": 45.00,
                "category": "gas",
                "recommended_card_id": "amex-blue-cash-preferred",
                "reward_earned": 1.35
            }
        ]
        
        for trans_data in demo_transactions:
            transaction = Transaction(**trans_data)
            db.add(transaction)
        
        db.commit()
        logger.info(f"Seeded {len(demo_cards)} demo cards and {len(demo_transactions)} transactions")
        
    except Exception as e:
        logger.error(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()
