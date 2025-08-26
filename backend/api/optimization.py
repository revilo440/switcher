"""
Main optimization endpoint - Natural language payment optimization
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
import logging
import json

from database.database import get_db, Card
from services.claude_service import ClaudeService
from services.brave_search_service import BraveSearchService
from services.card_optimizer import CardOptimizer
from services.fallback_responses import get_fallback_recommendation

logger = logging.getLogger(__name__)
router = APIRouter()

class OptimizationRequest(BaseModel):
    query: str
    user_context: Optional[str] = None

class OptimizationResponse(BaseModel):
    parsed_transaction: Dict[str, Any]
    market_analysis: Dict[str, Any]
    recommendation: Dict[str, Any]
    financial_insight: Dict[str, Any]

@router.post("/optimize")
async def optimize_payment(request: OptimizationRequest, db: Session = Depends(get_db)):
    """Main optimization endpoint with full market analysis"""
    try:
        logger.info(f"🚀 OPTIMIZATION REQUEST: '{request.query}'")
        
        # Initialize services
        claude_service = ClaudeService()
        brave_service = BraveSearchService()
        card_optimizer = CardOptimizer(claude_service, brave_service, db)
        
        # Parse the transaction
        logger.info("📝 STEP 1: Parsing transaction with Claude...")
        parsed_transaction = await claude_service.parse_transaction(request.query)
        if not parsed_transaction:
            logger.warning("❌ CLAUDE PARSING FAILED - using fallback")
            return get_fallback_recommendation(request.query)
        
        logger.info(f"✅ CLAUDE PARSED: {parsed_transaction}")
        
        # Get market analysis
        category = parsed_transaction.get("category", "general")
        logger.info(f"🔍 STEP 2: Searching market for category '{category}' with Brave...")
        
        market_analysis = await brave_service.discover_market_options(category)
        
        if market_analysis and market_analysis.get("results"):
            logger.info(f"✅ BRAVE SEARCH SUCCESS: Found {len(market_analysis.get('results', []))} results from {market_analysis.get('total_sources', 0)} sources")
            logger.info(f"🔗 BRAVE QUERIES USED: {market_analysis.get('queries_used', [])}")
        else:
            logger.warning("❌ BRAVE SEARCH FAILED OR EMPTY - proceeding with limited data")
        
        # Get recommendation
        logger.info("🧠 STEP 3: Generating recommendations with Claude...")
        
        # Extract discovered cards from market analysis
        discovered_cards = market_analysis.get("results", [])[:10]  # Limit for performance
        
        # Create research summary
        research_summary = {
            "total_sources": market_analysis.get("total_sources", 0),
            "queries_used": market_analysis.get("queries_used", []),
            "credible_sources": len([r for r in discovered_cards if r.get("credibility") == "high"])
        }
        
        recommendation = await claude_service.analyze_and_recommend(
            parsed_transaction, discovered_cards, research_summary
        )
        
        if recommendation:
            logger.info(f"✅ CLAUDE RECOMMENDATION SUCCESS: Best card = {recommendation.get('best_overall', {}).get('name', 'Unknown')}")
        else:
            logger.warning("❌ CLAUDE RECOMMENDATION FAILED")

        # Get financial insights
        logger.info("💰 STEP 4: Calculating financial impact...")
        financial_insight = card_optimizer.calculate_financial_impact(
            parsed_transaction, recommendation
        )
        
        logger.info("🎉 OPTIMIZATION COMPLETE - returning full analysis")
        
        return {
            "transaction": parsed_transaction,
            "market_analysis": market_analysis,
            "recommendation": recommendation,
            "financial_impact": financial_insight
        }
        
    except Exception as e:
        logger.error(f"Optimization error: {e}")
        # Return graceful fallback
        return get_fallback_recommendation(request.query)

