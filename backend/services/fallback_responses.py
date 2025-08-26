"""
Fallback responses for demo safety
"""
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

# Pre-configured fallback responses for demo scenarios
FALLBACK_RESPONSES = {
    "dining": {
        "parsed_transaction": {
            "merchant": "Restaurant",
            "amount": 25.00,
            "category": "dining",
            "confidence": 0.85,
            "ai_reasoning": "Dining purchase detected"
        },
        "market_analysis": {
            "cards_analyzed": 12,
            "data_sources": ["current offers", "signup bonuses"],
            "confidence": 0.9
        },
        "recommendation": {
            "best_overall": {
                "name": "Capital One Savor",
                "reward_amount": 0.22,
                "reward_rate": "4% cash back on dining",
                "annual_fee": 95,
                "signup_bonus": "$300 after $3k spend",
                "ai_reasoning": "Highest flat dining cash back rate",
                "data_source": "FALLBACK: Demo data (API unavailable)"
            },
            "runner_up": {
                "name": "Chase Sapphire Preferred",
                "reward_amount": 0.17,
                "reward_rate": "3x points on dining",
                "annual_fee": 95,
                "ai_reasoning": "Better for travel redemptions",
                "data_source": "FALLBACK: Demo data (API unavailable)"
            },
            "alternative": {
                "name": "Citi Double Cash",
                "reward_amount": 0.11,
                "reward_rate": "2% cash back on everything",
                "annual_fee": 0,
                "ai_reasoning": "Simple flat-rate cash back option",
                "data_source": "FALLBACK: Demo data (API unavailable)"
            },
            "opportunity_cost": "Missing $0.75 vs basic 2% card",
            "annual_projection": "Could earn $240/year on dining"
        },
        "financial_insight": {
            "opportunity_cost": "You're leaving $0.75 on the table",
            "annual_projection": "Could earn extra $240/year on dining"
        }
    },
    "grocery": {
        "parsed_transaction": {
            "merchant": "Grocery Store",
            "amount": 120.00,
            "category": "grocery",
            "confidence": 0.9,
            "ai_reasoning": "Grocery purchase identified"
        },
        "market_analysis": {
            "cards_analyzed": 15,
            "data_sources": ["market research", "bank websites"],
            "confidence": 0.95
        },
        "recommendation": {
            "best_overall": {
                "name": "Amex Blue Cash Preferred",
                "reward_amount": 0.36,
                "reward_rate": "6% cash back on groceries",
                "annual_fee": 95,
                "signup_bonus": "$300 after $3k spend",
                "ai_reasoning": "Highest grocery cash back rate",
                "data_source": "FALLBACK: Demo data (API unavailable)"
            },
            "runner_up": {
                "name": "Citi Custom Cash",
                "reward_amount": 0.30,
                "reward_rate": "5% on top category",
                "annual_fee": 0,
                "ai_reasoning": "No annual fee alternative",
                "data_source": "FALLBACK: Demo data (API unavailable)"
            },
            "alternative": {
                "name": "Chase Freedom Flex",
                "reward_amount": 0.24,
                "reward_rate": "5% rotating categories",
                "annual_fee": 0,
                "ai_reasoning": "Good when groceries are bonus category",
                "data_source": "FALLBACK: Demo data (API unavailable)"
            },
            "opportunity_cost": "Missing $4.80 vs basic 2% card",
            "annual_projection": "Could earn $864/year on groceries"
        },
        "financial_insight": {
            "opportunity_cost": "You're missing out on $4.80",
            "annual_projection": "Potential savings of $864/year"
        }
    },
    "travel": {
        "parsed_transaction": {
            "merchant": "Travel Purchase",
            "amount": 2000.00,
            "category": "travel",
            "confidence": 0.88,
            "ai_reasoning": "Travel expense detected"
        },
        "market_analysis": {
            "cards_analyzed": 18,
            "data_sources": ["travel sites", "card comparisons"],
            "confidence": 0.92
        },
        "recommendation": {
            "best_overall": {
                "name": "Capital One Venture X",
                "reward_amount": 40.00,
                "reward_rate": "2x miles on everything",
                "annual_fee": 395,
                "signup_bonus": "75,000 miles after $4k spend",
                "ai_reasoning": "Best overall travel rewards with lounge access"
            },
            "runner_up": {
                "name": "Chase Sapphire Reserve",
                "reward_amount": 60.00,
                "reward_rate": "3x points on travel",
                "annual_fee": 550,
                "ai_reasoning": "Higher multiplier but higher fee"
            },
            "alternative": {
                "name": "Wells Fargo Autograph",
                "reward_amount": 60.00,
                "reward_rate": "3x points on travel",
                "annual_fee": 0,
                "ai_reasoning": "No annual fee travel rewards option"
            },
            "opportunity_cost": "Missing $20 vs basic 2% card",
            "annual_projection": "Could earn $480/year on travel"
        },
        "financial_insight": {
            "opportunity_cost": "Leaving $20+ on the table",
            "annual_projection": "Annual travel rewards potential: $480+"
        }
    }
}

def get_fallback_recommendation(query: str) -> Dict[str, Any]:
    """Get appropriate fallback response based on query"""
    query_lower = query.lower()
    
    # Detect category from query
    if any(word in query_lower for word in ['coffee', 'starbucks', 'restaurant', 'dining', 'lunch', 'dinner']):
        response = FALLBACK_RESPONSES["dining"].copy()
    elif any(word in query_lower for word in ['grocery', 'whole foods', 'walmart', 'target', 'kroger']):
        response = FALLBACK_RESPONSES["grocery"].copy()
    elif any(word in query_lower for word in ['flight', 'hotel', 'travel', 'trip', 'vacation']):
        response = FALLBACK_RESPONSES["travel"].copy()
    else:
        # Generic fallback
        response = {
            "parsed_transaction": {
                "merchant": "Unknown",
                "amount": 100.00,
                "category": "shopping",
                "confidence": 0.7,
                "ai_reasoning": "General purchase detected"
            },
            "market_analysis": {
                "cards_analyzed": 10,
                "data_sources": ["demo mode"],
                "confidence": 0.8
            },
            "recommendation": {
                "best_overall": {
                    "name": "Citi Double Cash",
                    "reward_amount": 2.00,
                    "reward_rate": "2% cash back on everything",
                    "annual_fee": 0,
                    "signup_bonus": "$200 after $1.5k spend",
                    "ai_reasoning": "Best general purpose cash back"
                },
                "runner_up": {
                    "name": "Chase Freedom Unlimited",
                    "reward_amount": 1.50,
                    "reward_rate": "1.5% cash back",
                    "annual_fee": 0,
                    "ai_reasoning": "No annual fee alternative"
                },
                "alternative": {
                    "name": "Capital One Quicksilver",
                    "reward_amount": 1.50,
                    "reward_rate": "1.5% cash back",
                    "annual_fee": 0,
                    "ai_reasoning": "Simple cash back with no foreign transaction fees"
                },
                "opportunity_cost": "Optimized for general spending",
                "annual_projection": "Could earn $240/year"
            },
            "financial_insight": {
                "opportunity_cost": "Using optimal general card",
                "annual_projection": "Projected annual rewards: $240"
            }
        }
    
    # Helper to compute reward dollars from a reward_rate string and amount
    def compute_reward_amount(rate_str: str, amount: float) -> float:
        try:
            if not rate_str:
                return round(amount * 0.02, 2)
            s = rate_str.lower()
            import re
            pct = re.search(r'(\d+(?:\.\d+)?)\s*%\b', s)
            mult = re.search(r'(\d+(?:\.\d+)?)\s*x\b', s)
            if pct:
                rate = float(pct.group(1)) / 100.0
                return round(amount * rate, 2)
            if mult and ('point' in s or 'mile' in s):
                x = float(mult.group(1))
                # Use 1.5 cents per point/mile to align with compare_cards()
                point_value = 0.015
                # Points are earned per dollar (e.g., 3x points => 3 points per $1)
                # Convert points to dollars via point value
                return round(amount * x * point_value, 2)
            # Default baseline 2%
            return round(amount * 0.02, 2)
        except Exception:
            return round(amount * 0.02, 2)

    # Extract amount from query if present; otherwise use default in parsed_transaction
    import re
    amount_match = re.search(r'\$?([\d,]+\.?\d*)', query)
    if amount_match:
        try:
            amount = float(amount_match.group(1).replace(',', ''))
            response["parsed_transaction"]["amount"] = amount
        except ValueError:
            pass

    # Recalculate rewards uniformly for all recommendation entries based on parsed amount
    try:
        amount = float(response["parsed_transaction"].get("amount", 0) or 0)
        if amount > 0 and "recommendation" in response:
            for key in ["best_overall", "runner_up", "alternative"]:
                entry = response["recommendation"].get(key)
                if isinstance(entry, dict):
                    rate_str = entry.get("reward_rate", "")
                    entry["reward_amount"] = compute_reward_amount(rate_str, amount)
            # Ensure best_overall reflects highest net value among available entries
            entries = []
            for key in ["best_overall", "runner_up", "alternative"]:
                e = response["recommendation"].get(key)
                if isinstance(e, dict):
                    annual_fee = float(e.get("annual_fee", 0) or 0)
                    net_value = float(e.get("reward_amount", 0) or 0) - (annual_fee / 365.0)
                    entries.append((key, e, net_value))
            if len(entries) >= 2:
                entries.sort(key=lambda t: t[2], reverse=True)
                # Reassign best and runner up; keep alternative as the next if present
                response["recommendation"]["best_overall"] = entries[0][1]
                response["recommendation"]["runner_up"] = entries[1][1]
                if len(entries) > 2:
                    response["recommendation"]["alternative"] = entries[2][1]
    except Exception as e:
        logger.warning(f"Fallback reward recalculation skipped: {e}")

    logger.info("Using fallback recommendation")
    return response
