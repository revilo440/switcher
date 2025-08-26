"""
Core card optimization logic
"""
import json
import logging
from typing import Dict, Any, List
from sqlalchemy.orm import Session

from database.database import Card

logger = logging.getLogger(__name__)

class CardOptimizer:
    def __init__(self, claude_service, brave_service, db: Session):
        self.claude_service = claude_service
        self.brave_service = brave_service
        self.db = db
    
    def calculate_reward(self, card: Card, transaction: Dict) -> float:
        """Calculate reward amount for a transaction on a specific card"""
        try:
            reward_structure = json.loads(card.reward_structure)
            amount = transaction.get("amount", 0)
            category = transaction.get("category", "other")
            
            # Check category-specific rate
            category_rate = reward_structure.get("categories", {}).get(category)
            
            if category_rate:
                rate = category_rate
            else:
                # Use default rate
                rate = reward_structure.get("default_rate", 1.0)
            
            # Calculate reward
            reward_amount = amount * (rate / 100)
            
            # Apply point value conversion if applicable
            if reward_structure.get("reward_type") == "points":
                point_value = reward_structure.get("point_value", 0.01)
                reward_amount = reward_amount * point_value
            
            return round(reward_amount, 2)
            
        except Exception as e:
            logger.error(f"Error calculating reward: {e}")
            return 0.0
    
    def get_best_card_from_portfolio(self, transaction: Dict) -> Dict:
        """Get best card from user's existing portfolio"""
        cards = self.db.query(Card).filter(Card.is_active == True).all()
        
        best_card = None
        best_reward = 0
        
        for card in cards:
            reward = self.calculate_reward(card, transaction)
            if reward > best_reward:
                best_reward = reward
                best_card = card
        
        if best_card:
            reward_structure = json.loads(best_card.reward_structure)
            return {
                "card": best_card,
                "reward_amount": best_reward,
                "reward_structure": reward_structure
            }
        
        return None
    
    def compare_cards(self, cards: List[Dict], transaction: Dict) -> List[Dict]:
        """Compare multiple cards for a transaction"""
        comparisons = []
        
        for card_info in cards:
            # Parse rate to calculate reward
            rate_str = card_info.get("category_rate", "2%")
            
            # Extract numeric rate
            import re
            rate_match = re.search(r'(\d+(?:\.\d+)?)', rate_str)
            if rate_match:
                rate = float(rate_match.group(1))
            else:
                rate = 2.0  # Default 2%
            
            # Check if it's points or cash back
            is_points = 'point' in rate_str.lower() or 'mile' in rate_str.lower()
            
            # Calculate reward
            amount = transaction.get("amount", 0)
            if is_points:
                # Points are earned per dollar (e.g., 3x points => 3 points per $1)
                # Convert points to dollars using average 1.5 cents per point value
                reward_amount = amount * rate * 0.015
            else:
                reward_amount = amount * (rate / 100)
            
            comparisons.append({
                "card_name": card_info.get("card_name"),
                "issuer": card_info.get("issuer"),
                "reward_amount": round(reward_amount, 2),
                "reward_rate": card_info.get("category_rate"),
                "annual_fee": card_info.get("annual_fee", 0),
                "net_value": round(reward_amount - (card_info.get("annual_fee", 0) / 365), 2)  # Daily fee impact
            })
        
        # Sort by reward amount
        comparisons.sort(key=lambda x: x["reward_amount"], reverse=True)
        
        return comparisons
    
    def calculate_financial_impact(self, transaction: Dict, recommendation: Dict) -> Dict[str, Any]:
        """Calculate financial impact and insights"""
        try:
            if not recommendation:
                return {
                    "opportunity_cost": "Unable to calculate without recommendation",
                    "annual_projection": "Analysis unavailable"
                }
            
            best_card = recommendation.get("best_overall", {})
            reward_amount = best_card.get("reward_amount", 0)
            amount = transaction.get("amount", 0)
            category = transaction.get("category", "general")
            
            # Check for recurring purchase indicators
            query = transaction.get('original_query', '').lower()
            frequency_multiplier = 1
            frequency_text = ""
            
            if 'every week' in query or 'weekly' in query:
                frequency_multiplier = 52
                frequency_text = " (weekly purchases)"
            elif 'every month' in query or 'monthly' in query:
                frequency_multiplier = 12
                frequency_text = " (monthly purchases)"
            elif 'every day' in query or 'daily' in query:
                frequency_multiplier = 365
                frequency_text = " (daily purchases)"
            
            # Calculate opportunity cost vs basic 2% card
            basic_reward = amount * 0.02
            opportunity_cost = max(0, reward_amount - basic_reward)
            
            # Project annual savings based on frequency
            if frequency_multiplier > 1:
                # For recurring purchases, use actual frequency
                annual_estimate = amount * frequency_multiplier
            else:
                # For one-time purchases, estimate monthly spending
                monthly_estimate = amount * 4
                annual_estimate = monthly_estimate * 12
            
            # Calculate annual fee impact
            annual_fee = best_card.get("annual_fee", 0)
            annual_rewards = (reward_amount * frequency_multiplier) if frequency_multiplier > 1 else (annual_estimate * (reward_amount / amount if amount > 0 else 0))
            net_annual_benefit = annual_rewards - annual_fee
            
            return {
                "opportunity_cost": f"${opportunity_cost:.2f} more than basic 2% card",
                "annual_projection": f"Could earn ${net_annual_benefit:.0f}/year in {category} category{frequency_text}"
            }
            
        except Exception as e:
            logger.error(f"Financial impact calculation error: {e}")
            return {
                "opportunity_cost": "Calculation unavailable",
                "annual_projection": "Analysis unavailable"
            }
