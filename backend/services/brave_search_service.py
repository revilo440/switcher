"""
Brave Search API Service for market intelligence
"""
import os
import logging
from typing import List, Dict, Any
import asyncio
import aiohttp

logger = logging.getLogger(__name__)

class BraveSearchService:
    def __init__(self):
        self.api_key = os.getenv("BRAVE_SEARCH_API_KEY")
        if not self.api_key or self.api_key == "your_brave_api_key_here":
            logger.warning("Brave Search API key not configured - using fallback mode")
            self.api_key = None
        self.base_url = "https://api.search.brave.com/res/v1/web/search"
    
    async def search(self, query: str, count: int = 10) -> List[Dict[str, Any]]:
        """Perform a search using Brave Search API"""
        logger.info(f"🔍 BRAVE SEARCH: Attempting search for '{query}' (count={count})")
        
        if not self.api_key or self.api_key == "your_brave_api_key_here":
            logger.warning("❌ BRAVE API KEY NOT CONFIGURED - using fallback")
            return self._fallback_search_results(query)
        
        logger.info(f"🔑 BRAVE API KEY: Configured (ends with: ...{self.api_key[-4:]})")
        
        try:
            headers = {
                "Accept": "application/json",
                "Accept-Encoding": "gzip",
                "X-Subscription-Token": self.api_key
            }
            
            params = {
                "q": query,
                "count": count,
                "search_lang": "en",
                "country": "US",
                "safesearch": "moderate",
                "freshness": "pm"  # Past month for current info
            }
            
            logger.info(f"🌐 BRAVE REQUEST: {self.base_url} with params: {params}")
            
            timeout = aiohttp.ClientTimeout(total=8, connect=3, sock_read=5)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(self.base_url, headers=headers, params=params, timeout=timeout) as response:
                    logger.info(f"📡 BRAVE RESPONSE: Status {response.status}")
                    
                    if response.status == 200:
                        data = await response.json()
                        results = data.get("web", {}).get("results", [])
                        logger.info(f"✅ BRAVE SUCCESS: {len(results)} results returned")
                        
                        # Log first few results for debugging
                        for i, result in enumerate(results[:3]):
                            logger.info(f"   Result {i+1}: {result.get('title', 'No title')[:50]}...")
                        
                        return results
                    else:
                        response_text = await response.text()
                        logger.error(f"❌ BRAVE FAILED: Status {response.status}, Response: {response_text[:200]}...")
                        return self._fallback_search_results(query)
                        
        except Exception as e:
            logger.error(f"💥 BRAVE EXCEPTION: {str(e)}")
            return self._fallback_search_results(query)
    
    async def discover_market_options(self, category: str) -> Dict[str, Any]:
        """Phase 1: Broad market discovery for credit cards"""
        logger.info(f"🎯 MARKET DISCOVERY: Starting discovery for category '{category}'")
        
        discovery_queries = [
            f"best {category} credit cards 2025 cash back rewards comparison",
            f"highest {category} credit card rates December 2024",
            f"{category} credit cards 6% 5% 4% rewards current offers"
        ]
        
        logger.info(f"📋 DISCOVERY QUERIES: {discovery_queries}")
        
        all_results = []
        queries_used = []
        
        # Run discovery searches concurrently with per-call timeouts handled in self.search
        tasks = [asyncio.create_task(self.search(q, count=8)) for q in discovery_queries]
        results_list = await asyncio.gather(*tasks, return_exceptions=True)
        for q, res in zip(discovery_queries, results_list):
            if isinstance(res, Exception):
                logger.warning(f"Discovery search failed for '{q}': {res}")
                continue
            # Filter for credible sources
            filtered = self._filter_credible_sources(res)
            all_results.extend(filtered)
            queries_used.append(q)
        
        return {
            "results": all_results,
            "queries_used": queries_used,
            "total_sources": len(all_results)
        }
    
    async def research_specific_cards(self, card_candidates: List[Dict], transaction: Dict) -> Dict[str, Any]:
        """Phase 3: Targeted research on specific cards"""
        
        specific_queries = []
        
        # Research each discovered card (limit to top 3 for speed)
        for card in card_candidates[:3]:
            card_name = card.get("card_name", "")
            if card_name:
                specific_queries.extend([
                    f"{card_name} {transaction['category']} rewards rate annual fee 2024",
                    f"{card_name} signup bonus current December 2024"
                ])
        
        # Research merchant-specific considerations
        merchant = transaction.get("merchant", "")
        if merchant and merchant != "Unknown":
            specific_queries.append(
                f"{merchant} merchant category code MCC {transaction['category']}"
            )
        
        # Add general category bonus search
        specific_queries.append(
            f"{transaction['category']} credit cards signup bonuses December 2024"
        )
        
        # Execute targeted searches
        targeted_results = []
        for query in specific_queries[:5]:  # Limit queries for speed
            logger.info(f"Targeted search: {query}")
            results = await self.search(query, count=5)
            filtered = self._filter_credible_sources(results)
            targeted_results.extend(filtered)
        
        return {
            "results": targeted_results,
            "queries_executed": len(specific_queries),
            "cards_researched": len(card_candidates[:3])
        }
    
    def _filter_credible_sources(self, results: List[Dict]) -> List[Dict]:
        """Filter search results for credible financial sources"""
        credible_domains = [
            'nerdwallet.com', 'creditcards.com', 'thepointsguy.com',
            'bankrate.com', 'chase.com', 'americanexpress.com',
            'capitalone.com', 'citi.com', 'discover.com',
            'creditkarma.com', 'wallethub.com', 'usnews.com'
        ]
        
        filtered = []
        for result in results:
            url = result.get("url", "").lower()
            if any(domain in url for domain in credible_domains):
                result["credibility"] = "high"
                filtered.append(result)
            elif any(term in url for term in ['bank', 'credit', 'finance']):
                result["credibility"] = "medium"
                filtered.append(result)
        
        return filtered
    
    def _fallback_search_results(self, query: str) -> List[Dict]:
        """Fallback search results when API is not available"""
        logger.info(f"Using fallback search for: {query}")
        
        # Simulated search results for demo
        category_results = {
            "dining": [
                {
                    "title": "Best Dining Credit Cards 2024 - NerdWallet",
                    "url": "https://www.nerdwallet.com/best/credit-cards/dining",
                    "description": "Capital One Savor offers 4% cash back on dining. Chase Sapphire Preferred offers 3x points. Amex Gold offers 4x points on restaurants.",
                    "credibility": "high"
                },
                {
                    "title": "Top Restaurant Rewards Cards - The Points Guy",
                    "url": "https://thepointsguy.com/guide/best-dining-credit-cards/",
                    "description": "Comprehensive comparison of dining rewards cards. Capital One Savor leads with unlimited 4% cash back.",
                    "credibility": "high"
                }
            ],
            "grocery": [
                {
                    "title": "Best Grocery Credit Cards December 2024",
                    "url": "https://www.creditcards.com/best/grocery-rewards/",
                    "description": "Amex Blue Cash Preferred offers 6% cash back on groceries up to $6,000/year. Amex Gold offers 4x points.",
                    "credibility": "high"
                },
                {
                    "title": "Highest Grocery Cash Back Cards - Bankrate",
                    "url": "https://www.bankrate.com/credit-cards/rewards/best-grocery/",
                    "description": "Blue Cash Preferred leads with 6% back. Citi Custom Cash offers 5% on top category.",
                    "credibility": "high"
                }
            ],
            "travel": [
                {
                    "title": "Best Travel Credit Cards 2024",
                    "url": "https://www.nerdwallet.com/best/credit-cards/travel",
                    "description": "Chase Sapphire Reserve offers 3x on travel. Capital One Venture X offers 2x miles on everything.",
                    "credibility": "high"
                },
                {
                    "title": "Premium Travel Cards Comparison",
                    "url": "https://thepointsguy.com/guide/best-travel-credit-cards/",
                    "description": "Comprehensive guide to travel rewards cards with current signup bonuses.",
                    "credibility": "high"
                }
            ]
        }
        
        # Extract category from query
        query_lower = query.lower()
        for category, results in category_results.items():
            if category in query_lower:
                return results
        
        # Default fallback
        return [
            {
                "title": "Best Cash Back Credit Cards 2024",
                "url": "https://www.nerdwallet.com/best/credit-cards/cash-back",
                "description": "Citi Double Cash offers 2% on everything. Wells Fargo Active Cash offers 2% unlimited.",
                "credibility": "high"
            }
        ]
