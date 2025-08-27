"""
Database configuration and initialization
"""
import os
import json
import logging
from datetime import datetime

from sqlalchemy import create_engine, Column, String, Float, Integer, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from sqlalchemy.exc import IntegrityError

logger = logging.getLogger(__name__)

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./payment_optimizer.db")

engine_kwargs = {}
if DATABASE_URL.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}
engine = create_engine(DATABASE_URL, **engine_kwargs)
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
    """Seed database with demo credit cards (idempotent and race-safe)"""
    db = SessionLocal()
    try:
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

        inserted_cards = 0
        for card_data in demo_cards:
            cid = card_data["id"]
            try:
                if db.get(Card, cid) is None:
                    db.add(Card(**card_data))
                    db.commit()
                    inserted_cards += 1
            except IntegrityError:
                db.rollback()
                logger.info(f"Card '{cid}' already present; skipping...")
            except Exception as e:
                db.rollback()
                logger.error(f"Error inserting card '{cid}': {e}")
        
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

        inserted_txns = 0
        for t in demo_transactions:
            #only add if recommended card exists
            if db.get(Card, t["recommended_card_id"]) is None:
                logger.info(f"Recommended card '{t['recommended_card_id']}' not found; skipping transaction...")
                continue
            try:
                db.add(Transaction(**t))
                db.commit()
                inserted_txns += 1
            except IntegrityError:
                db.rollback()
                logger.info(f"Transaction '{t['merchant']}' already present; skipping...")
            except Exception as e:
                db.rollback()
                logger.error(f"Error inserting transaction '{t['merchant']}': {e}")
                
        logger.info(f"Seed complete: {inserted_cards} demo cards and {inserted_txns} demo transactions")
    except Exception as e:
        logger.error(f"Error seeding demo data: {e}")
        db.rollback()
    finally:
        db.close()
