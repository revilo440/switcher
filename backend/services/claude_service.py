"""
Claude API Service for NL parsing and analysis
"""
import os
import json
import logging
from typing import Dict, Any, List, Optional
import anthropic
from anthropic import AsyncAnthropic
import asyncio

logger = logging.getLogger(__name__)

class ClaudeService:
    def __init__(self):
        api_key = os.getenv("CLAUDE_API_KEY")
        if not api_key or api_key == "your_claude_api_key_here":
            logger.warning("Claude API key not configured - using fallback mode")
            self.client = None
        else:
            self.client = AsyncAnthropic(api_key=api_key)
    
    async def parse_transaction(self, query: str) -> Dict[str, Any]:
        """Parse natural language transaction into structured data"""
        
        if not self.client:
            # Fallback parsing without API
            return self._fallback_parse(query)
        
        prompt = f"""Parse this financial transaction request and extract structured data:
"{query}"

Return ONLY valid JSON with these fields:
{{
    "merchant": "exact merchant name or 'Unknown' if not specified",
    "amount": numeric_amount_or_0,
    "category": "one of: dining, grocery, gas, travel, entertainment, shopping, utilities, healthcare, other",
    "confidence": 0.0-1.0,
    "extracted_context": ["additional context about merchant/purchase"],
    "ai_reasoning": "brief explanation of parsing decisions"
}}

Examples:
- "buying $5.50 coffee at Starbucks" -> dining category, high confidence
- "grocery shopping $120 at Whole Foods" -> grocery category, high confidence
- "planning $2000 Europe trip" -> travel category, high confidence
"""
        
        try:
            response = await asyncio.wait_for(self.client.messages.create(
                model="claude-3-5-haiku-latest",
                max_tokens=500,
                temperature=0,
                messages=[{"role": "user", "content": prompt}]
            ), timeout=8)
            
            # Parse JSON from response
            result = json.loads(response.content[0].text)
            result['confidence'] = result.get('confidence', 0.95)
            result['original_query'] = query  # Store original query for recurring detection
            logger.info(f"Parsed transaction: {result}")
            return result
            
        except asyncio.TimeoutError:
            logger.error("Claude API timeout during parse_transaction; using fallback parse")
            return self._fallback_parse(query)
        except Exception as e:
            logger.error(f"Claude API error: {e}")
            return self._fallback_parse(query)
    
    async def extract_discovered_cards(self, discovery_results: List[Dict], category: str) -> List[Dict]:
        """Extract specific credit cards from market discovery results"""
        
        if not self.client:
            return self._fallback_cards(category)
        
        # Combine discovery results into text
        results_text = "\n".join([
            f"Source: {r.get('title', '')}\n{r.get('description', '')}"
            for r in discovery_results[:10]
        ])
        
        prompt = f"""Analyze these market research results about {category} credit cards and extract specific card options:

Search Results:
{results_text}

Extract all credit cards mentioned with their reward structures. Return JSON array:
[
    {{
        "card_name": "full official name",
        "issuer": "bank name",
        "category_rate": "specific {category} reward rate",
        "annual_fee": "fee amount or 0",
        "spending_cap": "any annual/monthly limits or null",
        "promotional_offers": "current signup bonuses or limited-time rates",
        "source_quality": "high/medium/low based on source credibility"
    }}
]

Only include cards with specific {category} rewards. Focus on major issuers (Chase, Amex, Citi, Capital One, etc.).
Be precise about rates - distinguish between temporary promotional rates and standard rates."""
        
        try:
            response = await asyncio.wait_for(self.client.messages.create(
                model="claude-3-5-haiku-latest",
                max_tokens=1000,
                temperature=0,
                messages=[{"role": "user", "content": prompt}]
            ), timeout=10)
            
            result = json.loads(response.content[0].text)
            logger.info(f"Extracted {len(result)} cards from discovery")
            return result
            
        except asyncio.TimeoutError:
            logger.error("Claude API timeout during extract_discovered_cards; using fallback cards")
            return self._fallback_cards(category)
        except Exception as e:
            logger.error(f"Card extraction error: {e}")
            return self._fallback_cards(category)
    
    async def analyze_and_recommend(self, transaction: Dict, discovered_cards: List[Dict], research: Dict) -> Dict:
        """Provide final AI financial analysis and recommendation"""
        
        if not self.client:
            return self._fallback_recommendation(transaction)
        
        # Check for recurring purchase indicators
        query_lower = transaction.get('original_query', '').lower()
        is_recurring = any(term in query_lower for term in ['every', 'weekly', 'monthly', 'daily', 'recurring', 'regular'])
        frequency_multiplier = 1
        if 'every week' in query_lower or 'weekly' in query_lower:
            frequency_multiplier = 52
        elif 'every month' in query_lower or 'monthly' in query_lower:
            frequency_multiplier = 12
        elif 'every day' in query_lower or 'daily' in query_lower:
            frequency_multiplier = 365
        
        prompt = f"""You are an expert financial advisor. Based on the transaction details and market research data, analyze and recommend the best credit cards.

Transaction: {json.dumps(transaction)}
Discovered Cards: {json.dumps(discovered_cards[:5])}  
Research Summary: {json.dumps(research)}
{f"Recurring Purchase: Yes, estimated {frequency_multiplier} times per year" if is_recurring else ""}

CRITICAL EVALUATION CRITERIA - FOLLOW THESE RULES EXACTLY:
1. Calculate reward amount for EACH card
2. Compare: Card A gives ${transaction.get('amount', 0) * 0.05:.2f} with $0 fee vs Card B gives ${transaction.get('amount', 0) * 0.03:.2f} with $95 fee
3. For single purchases: The card with HIGHER REWARD AMOUNT and LOWER/NO FEE wins
4. For recurring purchases: Calculate (reward_per_transaction * {frequency_multiplier}) - annual_fee
5. **IMPORTANT**: If Card A gives 5% ($2.25) with $0 fee and Card B gives 3% ($1.35) with $95 fee, Card A MUST be "best_overall"
6. The "best_overall" MUST be the card that gives the user the MOST MONEY BACK considering fees

Consider:
1. Reward rates for this specific category
2. Annual fees vs benefits (CRITICAL: Don't recommend high fee cards unless rewards justify it)
3. Signup bonuses and current offers
4. Merchant category considerations
5. Spending caps and limitations (especially for high % cards like 5% with monthly caps)

IMPORTANT: Return ONLY valid JSON, no other text. Use this exact format:
{{
    "best_overall": {{
        "name": "card name",
        "reward_amount": calculated_reward_in_dollars,
        "reward_rate": "rate description",
        "annual_fee": fee_amount,
        "signup_bonus": "bonus description if available",
        "ai_reasoning": "why this is best for this purchase",
        "calculation_logic": "show the math: e.g., $5.50 × 4% = $0.22 cash back OR $5.50 × 3 points × $0.015/point = $0.25",
        "data_source": "specific URL or source where this info was found"
    }},
    "runner_up": {{
        "name": "card name",
        "reward_amount": calculated_reward_in_dollars,
        "reward_rate": "rate description",
        "annual_fee": fee_amount,
        "ai_reasoning": "why this is second best",
        "calculation_logic": "show the math for this card",
        "data_source": "specific URL or source where this info was found"
    }},
    "alternative": {{
        "name": "card name",
        "reward_amount": calculated_reward_in_dollars,
        "reward_rate": "rate description",
        "annual_fee": fee_amount,
        "ai_reasoning": "why this is a good alternative option",
        "calculation_logic": "show the math for this card",
        "data_source": "specific URL or source where this info was found"
    }},
    "opportunity_cost": "comparison to average 2% card",
    "annual_projection": "NOT about future earnings - focus on comparison to other cards",
    "data_freshness": "how recent the market data is"
}}

CRITICAL: For reward calculations:
- Cash back: multiply purchase amount by percentage (e.g., $100 × 4% = $4.00)
- Points: multiply purchase amount by points rate, then by point value (e.g., $100 × 3 points × $0.01/point = $3.00)
- Use realistic point values: Chase UR ~1.5¢, Amex MR ~1.8¢, airline miles ~1.2¢, hotel points ~0.6¢
- Always show your calculation in calculation_logic field
- For "best_overall": MUST be the card with highest net value (rewards minus fees)
- EXAMPLE: 5% back with $0 fee ALWAYS beats 3% back with $95 fee for gas purchases
- DO NOT recommend high annual fee cards as "best" unless the rewards FAR exceed the fee
- The runner_up should be the second-best option, not the best option
- IMPORTANT: reward_amount must be a NUMBER, not a formula. Calculate the actual value."""
        
        try:
            response = await asyncio.wait_for(self.client.messages.create(
                model="claude-3-5-haiku-latest",
                max_tokens=1000,
                temperature=0,
                messages=[{"role": "user", "content": prompt}]
            ), timeout=12)
            
            response_text = response.content[0].text
            logger.info(f"Claude response: {response_text[:200]}...")
            
            # Try to extract JSON from response (in case Claude adds extra text)
            try:
                result = json.loads(response_text)
            except json.JSONDecodeError:
                # Try to find JSON within the response
                import re
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group())
                else:
                    raise
            
            # Ensure consistent field naming and add missing fields
            if result.get("best_overall"):
                # Rename 'name' to 'card_name' for consistency
                if "name" in result["best_overall"] and "card_name" not in result["best_overall"]:
                    result["best_overall"]["card_name"] = result["best_overall"]["name"]
                # Rename 'reward_amount' to 'reward_value' for consistency
                if "reward_amount" in result["best_overall"] and "reward_value" not in result["best_overall"]:
                    result["best_overall"]["reward_value"] = result["best_overall"]["reward_amount"]
                # Add source attribution if missing
                if not result["best_overall"].get("data_source"):
                    result["best_overall"]["data_source"] = f"Live market data from {len(discovered_cards)} sources"
            
            if result.get("runner_up"):
                # Rename 'name' to 'card_name' for consistency
                if "name" in result["runner_up"] and "card_name" not in result["runner_up"]:
                    result["runner_up"]["card_name"] = result["runner_up"]["name"]
                # Rename 'reward_amount' to 'reward_value' for consistency
                if "reward_amount" in result["runner_up"] and "reward_value" not in result["runner_up"]:
                    result["runner_up"]["reward_value"] = result["runner_up"]["reward_amount"]
                # Add source attribution if missing
                if not result["runner_up"].get("data_source"):
                    result["runner_up"]["data_source"] = f"Live market data from {len(discovered_cards)} sources"
            
            if result.get("alternative"):
                # Rename 'name' to 'card_name' for consistency
                if "name" in result["alternative"] and "card_name" not in result["alternative"]:
                    result["alternative"]["card_name"] = result["alternative"]["name"]
                # Rename 'reward_amount' to 'reward_value' for consistency
                if "reward_amount" in result["alternative"] and "reward_value" not in result["alternative"]:
                    result["alternative"]["reward_value"] = result["alternative"]["reward_amount"]
                # Add source attribution if missing
                if not result["alternative"].get("data_source"):
                    result["alternative"]["data_source"] = f"Live market data from {len(discovered_cards)} sources"
            
            # Post-process to ensure correct card ordering based on net value
            best = result.get("best_overall", {})
            runner = result.get("runner_up", {})
            
            # Calculate net values for comparison
            best_reward = best.get("reward_amount", 0)
            best_fee = best.get("annual_fee", 0)
            runner_reward = runner.get("reward_amount", 0) 
            runner_fee = runner.get("annual_fee", 0)
            
            # Check for recurring purchases
            query_lower = transaction.get('original_query', '').lower()
            frequency = 1
            if 'every week' in query_lower or 'weekly' in query_lower:
                frequency = 52
            elif 'every month' in query_lower or 'monthly' in query_lower:
                frequency = 12
            elif 'every day' in query_lower or 'daily' in query_lower:
                frequency = 365
            
            # Calculate annual net value
            best_net = (best_reward * frequency) - best_fee
            runner_net = (runner_reward * frequency) - runner_fee
            
            # Swap if runner-up is actually better
            if runner_net > best_net and runner_reward > 0:
                result["best_overall"], result["runner_up"] = result["runner_up"], result["best_overall"]
                # Update reasoning
                result["best_overall"]["ai_reasoning"] = f"Higher net value: ${runner_reward:.2f} per transaction with ${runner_fee} annual fee beats ${best_reward:.2f} with ${best_fee} fee"
                result["runner_up"]["ai_reasoning"] = "Lower net value despite good rewards"
            
            # Ensure consistent field naming and add missing fields
            if result.get("best_overall"):
                # Add card_name and reward_value for consistency
                result["best_overall"]["card_name"] = result["best_overall"].get("name", "Unknown Card")
                result["best_overall"]["reward_value"] = result["best_overall"].get("reward_amount", 0)
                
            if result.get("runner_up"):
                result["runner_up"]["card_name"] = result["runner_up"].get("name", "Unknown Card")
                result["runner_up"]["reward_value"] = result["runner_up"].get("reward_amount", 0)
            
            if result.get("alternative"):
                result["alternative"]["card_name"] = result["alternative"].get("name", "Unknown Card")
                result["alternative"]["reward_value"] = result["alternative"].get("reward_amount", 0)
            
            # Add top-level fields for easier access
            if result.get("best_overall"):
                result["card_name"] = result["best_overall"]["card_name"]
                result["reward_value"] = result["best_overall"]["reward_value"]
                result["calculation_logic"] = result["best_overall"].get("calculation_logic", "")
                result["data_source"] = result["best_overall"].get("data_source", "AI Analysis")
                result["reward_rate"] = result["best_overall"].get("reward_rate", "")
                result["calculation_method"] = "AI-analyzed market rates × purchase amount"
            
            # Ensure source attribution
            if "data_source" not in result:
                result["data_source"] = "AI Analysis"
            
            logger.info("Generated AI recommendation with source attribution")
            logger.info(f"Best card reward: ${result.get('reward_value', 0):.2f}")
            return result
            
        except asyncio.TimeoutError:
            logger.error("Claude API timeout during analyze_and_recommend; using fallback recommendation")
            return self._fallback_recommendation(transaction)
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            logger.error(f"Raw response: {response_text[:500]}")
            return self._fallback_recommendation(transaction)
        except Exception as e:
            logger.error(f"Recommendation error: {e}")
            return self._fallback_recommendation(transaction)
    
    def _fallback_parse(self, user_input: str) -> Dict[str, Any]:
        """Fallback parsing without API"""
        # Simple keyword-based parsing
        amount = 0
        merchant = "Unknown"
        category = "other"
        
        # Extract amount
        import re
        amount_match = re.search(r'\$?([\d,]+\.?\d*)', user_input)
        if amount_match:
            amount = float(amount_match.group(1).replace(',', ''))
        
        # Detect category and merchant
        input_lower = user_input.lower()
        
        if any(word in input_lower for word in ['starbucks', 'coffee', 'cafe', 'restaurant', 'dining']):
            category = "dining"
            if 'starbucks' in input_lower:
                merchant = "Starbucks"
        elif any(word in input_lower for word in ['grocery', 'whole foods', 'walmart', 'target']):
            category = "grocery"
            if 'whole foods' in input_lower:
                merchant = "Whole Foods"
        elif any(word in input_lower for word in ['gas', 'shell', 'exxon', 'chevron']):
            category = "gas"
        elif any(word in input_lower for word in ['flight', 'hotel', 'travel', 'trip', 'airline']):
            category = "travel"
        
        return {
            "merchant": merchant,
            "amount": amount,
            "category": category,
            "confidence": 0.7,
            "extracted_context": ["Parsed without API"],
            "ai_reasoning": "Fallback keyword-based parsing"
        }
    
    def _fallback_cards(self, category: str) -> List[Dict]:
        """Fallback card recommendations by category"""
        cards_by_category = {
            "dining": [
                {
                    "card_name": "Capital One Savor",
                    "issuer": "Capital One",
                    "category_rate": "4% cash back",
                    "annual_fee": 95,
                    "spending_cap": None,
                    "promotional_offers": "$300 bonus after $3k spend",
                    "source_quality": "high"
                },
                {
                    "card_name": "Chase Sapphire Preferred",
                    "issuer": "Chase",
                    "category_rate": "3x points",
                    "annual_fee": 95,
                    "spending_cap": None,
                    "promotional_offers": "60k points after $4k spend",
                    "source_quality": "high"
                }
            ],
            "grocery": [
                {
                    "card_name": "Amex Blue Cash Preferred",
                    "issuer": "American Express",
                    "category_rate": "6% cash back",
                    "annual_fee": 95,
                    "spending_cap": "$6,000/year",
                    "promotional_offers": "$350 after $3k spend",
                    "source_quality": "high"
                },
                {
                    "card_name": "Amex Gold Card",
                    "issuer": "American Express",
                    "category_rate": "4x points",
                    "annual_fee": 250,
                    "spending_cap": "$25,000/year",
                    "promotional_offers": "90k points after $6k spend",
                    "source_quality": "high"
                }
            ],
            "travel": [
                {
                    "card_name": "Capital One Venture X",
                    "issuer": "Capital One",
                    "category_rate": "2x miles on everything",
                    "annual_fee": 395,
                    "spending_cap": None,
                    "promotional_offers": "75k miles after $4k spend",
                    "source_quality": "high"
                },
                {
                    "card_name": "Chase Sapphire Reserve",
                    "issuer": "Chase",
                    "category_rate": "3x points",
                    "annual_fee": 550,
                    "spending_cap": None,
                    "promotional_offers": "60k points after $4k spend",
                    "source_quality": "high"
                }
            ]
        }
        
        return cards_by_category.get(category, [
            {
                "card_name": "Citi Double Cash",
                "issuer": "Citi",
                "category_rate": "2% cash back",
                "annual_fee": 0,
                "spending_cap": None,
                "promotional_offers": "$200 after $1.5k spend",
                "source_quality": "medium"
            }
        ])
    
    def _fallback_recommendation(self, transaction: Dict) -> Dict:
        """Fallback recommendation without API"""
        category = transaction.get("category", "other")
        amount = transaction.get("amount", 100)
        
        recommendations = {
            "dining": {
                "best_overall": {
                    "name": "Capital One Savor",
                    "reward_amount": round(amount * 0.04, 2),
                    "reward_rate": "4% cash back on dining",
                    "annual_fee": 95,
                    "signup_bonus": "$300 after $3k spend",
                    "ai_reasoning": "Highest flat dining cash back rate available"
                },
                "runner_up": {
                    "name": "Chase Sapphire Preferred",
                    "reward_amount": round(amount * 0.03, 2),
                    "reward_rate": "3x points on dining",
                    "annual_fee": 95,
                    "ai_reasoning": "Better for travel redemptions"
                }
            },
            "grocery": {
                "best_overall": {
                    "name": "Amex Blue Cash Preferred",
                    "reward_amount": round(amount * 0.06, 2),
                    "reward_rate": "6% cash back on groceries",
                    "annual_fee": 95,
                    "signup_bonus": "$350 after $3k spend",
                    "ai_reasoning": "Highest grocery cash back rate in market"
                },
                "runner_up": {
                    "name": "Amex Gold Card",
                    "reward_amount": round(amount * 0.04, 2),
                    "reward_rate": "4x points on groceries",
                    "annual_fee": 250,
                    "ai_reasoning": "Better for premium travel redemptions"
                }
            }
        }
        
        rec = recommendations.get(category, {
            "best_overall": {
                "name": "Citi Double Cash",
                "reward_amount": round(amount * 0.02, 2),
                "reward_rate": "2% cash back on everything",
                "annual_fee": 0,
                "signup_bonus": "$200 after $1.5k spend",
                "ai_reasoning": "Best general purpose cash back card"
            },
            "runner_up": {
                "name": "Chase Freedom Unlimited",
                "reward_amount": round(amount * 0.015, 2),
                "reward_rate": "1.5% cash back",
                "annual_fee": 0,
                "ai_reasoning": "No annual fee option"
            }
        })
        
        # Helper to compute reward dollars from a reward_rate string and amount
        def compute_reward_amount(rate_str: str, amt: float) -> float:
            try:
                if not rate_str:
                    return round(amt * 0.02, 2)
                s = rate_str.lower()
                import re
                pct = re.search(r'(\d+(?:\.\d+)?)\s*%\b', s)
                mult = re.search(r'(\d+(?:\.\d+)?)\s*x\b', s)
                if pct:
                    rate = float(pct.group(1)) / 100.0
                    return round(amt * rate, 2)
                if mult and ('point' in s or 'mile' in s):
                    x = float(mult.group(1))
                    point_value = 0.015  # 1.5 cents/point
                    return round(amt * x * point_value, 2)
                return round(amt * 0.02, 2)
            except Exception:
                return round(amt * 0.02, 2)

        # Recalculate from reward_rate strings to ensure correctness
        try:
            for key in ["best_overall", "runner_up", "alternative"]:
                entry = rec.get(key)
                if isinstance(entry, dict):
                    entry["reward_amount"] = compute_reward_amount(entry.get("reward_rate", ""), amount)

            # Reorder best/runner_up by net value (reward - fee/365)
            best = rec.get("best_overall", {})
            runner = rec.get("runner_up", {})
            if isinstance(best, dict) and isinstance(runner, dict):
                best_net = float(best.get("reward_amount", 0) or 0) - float(best.get("annual_fee", 0) or 0) / 365.0
                runner_net = float(runner.get("reward_amount", 0) or 0) - float(runner.get("annual_fee", 0) or 0) / 365.0
                if runner_net > best_net and runner.get("reward_amount", 0) > 0:
                    rec["best_overall"], rec["runner_up"] = runner, best
                    rec["best_overall"]["ai_reasoning"] = (
                        rec["best_overall"].get("ai_reasoning", "")
                        + " | Higher net value for this purchase"
                    ).strip()
        except Exception:
            pass

        rec["opportunity_cost"] = f"Missing ${round(rec['best_overall']['reward_amount'] - amount * 0.01, 2)} vs 1% card"
        rec["annual_projection"] = f"Could earn ${round(rec['best_overall']['reward_amount'] * 12, 2)}/year at this rate"
        
        return rec
