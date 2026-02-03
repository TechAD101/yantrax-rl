"""Knowledge Base Service

Vector database service using ChromaDB for storing and retrieving:
- Investor wisdom (Buffett, Dalio, Hindi proverbs)
- Strategy performance history
- Market insights and playbooks

Provides semantic search for persona context enrichment.
"""

import chromadb
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import os


class KnowledgeBaseService:
    """
    ChromaDB-powered knowledge base for investor wisdom and market insights
    
    Collections:
    - investor_wisdom: Legendary investor quotes and principles
    - strategy_performance: Historical trade outcomes and learnings
    - market_insights: Market patterns, regimes, and playbooks
    """
    
    def __init__(self, persist_directory: str = "./chroma_db"):
        """
        Initialize ChromaDB client and collections
        
        Args:
            persist_directory: Local directory for ChromaDB persistence
        """
        self.logger = logging.getLogger(__name__)
        self.persist_directory = persist_directory
        
        # Create persist directory if it doesn't exist
        os.makedirs(persist_directory, exist_ok=True)
        
        # Initialize ChromaDB client with current API
        try:
            self.client = chromadb.PersistentClient(path=persist_directory)
            self.logger.info(f"✓ ChromaDB client initialized at {persist_directory}")
        except Exception as e:
            self.logger.error(f"Failed to initialize ChromaDB: {e}")
            raise
        
        self.collections = {}
        self._initialize_collections()
        
        # Seed if empty
        if self.collections['investor_wisdom'].count() == 0:
            self._seed_wisdom()
    
    def _seed_wisdom(self):
        """Seed the KB with foundational investment lore"""
        wisdom = [
             {
                "content": "Rule No. 1: Never lose money. Rule No. 2: Never forget rule No. 1.",
                "source": "Warren Buffett",
                "tags": ["survival"],
                "archetype": ["warren"]
            },
            {
                "content": "Be fearful when others are greedy and greedy when others are fearful.",
                "source": "Warren Buffett",
                "tags": ["sentiment"],
                "archetype": ["warren"]
            },
            {
                "content": "If you don't own gold, you know neither history nor economics.",
                "source": "Ray Dalio",
                "tags": ["macro"],
                "archetype": ["macros"]
            },
            {
                "content": "Pain + Reflection = Progress.",
                "source": "Ray Dalio",
                "tags": ["mindset"],
                "archetype": ["philosopher"]
            },
            {
                "content": "The big money is not in the buying and the selling, but in the waiting.",
                "source": "Charlie Munger",
                "tags": ["patience"],
                "archetype": ["warren"]
            },
            {
                "content": "The market is a mirror of collective emotion. It does not think, it feels.",
                "source": "The Ghost",
                "tags": ["quantum_meta"],
                "archetype": ["ghost"]
            },
            {
                "content": "Chalti ka naam gaadi (Only that which moves is a car/working). Momentum is king.",
                "source": "Hindi Wisdom",
                "tags": ["momentum"],
                "archetype": ["quant"]
            },
            {
                "content": "Boond boond se ghada bharta hai (Drop by drop the pot fills). Consistent small gains.",
                "source": "Hindi Wisdom",
                "tags": ["compounding"],
                "archetype": ["warren"]
            },
            {
                "content": "The trend is your friend until the end when it bends.",
                "source": "Ed Seykota",
                "tags": ["trend", "momentum"],
                "archetype": ["quant", "cathie"]
            },
            {
                "content": "In trading, you have to be defensive and aggressive at the same time. If you are not aggressive, you are not going to make money; and if you are not defensive, you are not going to keep money.",
                "source": "Paul Tudor Jones",
                "tags": ["risk_management", "defense"],
                "archetype": ["macros", "degen_auditor"]
            },
            {
                "content": "Markets can remain irrational longer than you can remain solvent.",
                "source": "John Maynard Keynes",
                "tags": ["irrationality", "margin"],
                "archetype": ["philosopher", "ghost"]
            },
            {
                "content": "The most important quality for an investor is temperament, not intellect.",
                "source": "Warren Buffett",
                "tags": ["psychology", "patience"],
                "archetype": ["warren"]
            },
            {
                "content": "Everything is a paradox. The more certain the crowd is, the more likely the surprise.",
                "source": "The Ghost",
                "tags": ["paradox", "contrarian"],
                "archetype": ["ghost"]
            }
        ]
        
        for item in wisdom:
            self.store_wisdom(
                content=item["content"],
                source=item["source"],
                tags=item["tags"],
                archetype=item["archetype"]
            )
        self.logger.info(f"🌱 Seeded Knowledge Base with {len(wisdom)} core principles.")

    def _initialize_collections(self):
        """Create or load ChromaDB collections"""
        try:
            self.collections['investor_wisdom'] = self.client.get_or_create_collection(
                name="investor_wisdom",
                metadata={"description": "Legendary investor quotes and wisdom"}
            )
            self.logger.info("✓ investor_wisdom collection ready")
            
            self.collections['strategy_performance'] = self.client.get_or_create_collection(
                name="strategy_performance",
                metadata={"description": "Historical strategy outcomes and learnings"}
            )
            self.logger.info("✓ strategy_performance collection ready")
            
            self.collections['market_insights'] = self.client.get_or_create_collection(
                name="market_insights",
                metadata={"description": "Market patterns, regimes, and playbooks"}
            )
            self.logger.info("✓ market_insights collection ready")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize collections: {e}")
            raise
    
    def store_wisdom(self, content: str, source: str, tags: List[str], 
                    archetype: List[str], confidence: float = 0.9,
                    **metadata) -> str:
        """
        Store wisdom item in investor_wisdom collection
        
        Args:
            content: The wisdom/quote text
            source: Source attribution (e.g., "Warren Buffett")
            tags: Categorization tags (e.g., ["risk_management", "contrarian"])
            archetype: Relevant persona archetypes (e.g., ["warren", "quant"])
            confidence: Confidence score (0-1)
            **metadata: Additional metadata (book, chapter, etc.)
        
        Returns:
            Document ID
        """
        collection = self.collections['investor_wisdom']
        doc_id = f"wisdom_{collection.count() + 1:04d}"
        
        try:
            collection.add(
                documents=[content],
                metadatas=[{
                    "source": source,
                    "tags": ",".join(tags),
                    "archetype": ",".join(archetype),
                    "confidence": confidence,
                    "created_at": datetime.now().isoformat(),
                    **metadata
                }],
                ids=[doc_id]
            )
            self.logger.debug(f"✓ Stored wisdom: {doc_id}")
            return doc_id
        except Exception as e:
            self.logger.error(f"Failed to store wisdom: {e}")
            raise
    
    def store_strategy_result(self, strategy_name: str, outcome: str, 
                             context: Dict[str, Any], lessons: str,
                             **metadata) -> str:
        """
        Store strategy performance result
        
        Args:
            strategy_name: Name of strategy (e.g., "momentum_scalp")
            outcome: Result (e.g., "success", "failure", "learning")
            context: Market context dict
            lessons: Key learnings from this execution
            **metadata: Additional metadata
        
        Returns:
            Document ID
        """
        collection = self.collections['strategy_performance']
        doc_id = f"strategy_{collection.count() + 1:04d}"
        
        try:
            # Create searchable content
            content = f"Strategy: {strategy_name}. Outcome: {outcome}. Lessons: {lessons}"
            
            collection.add(
                documents=[content],
                metadatas=[{
                    "strategy_name": strategy_name,
                    "outcome": outcome,
                    "market_trend": context.get('market_trend', 'unknown'),
                    "volatility": str(context.get('volatility', 0)),
                    "timestamp": datetime.now().isoformat(),
                    **metadata
                }],
                ids=[doc_id]
            )
            self.logger.debug(f"✓ Stored strategy result: {doc_id}")
            return doc_id
        except Exception as e:
            self.logger.error(f"Failed to store strategy result: {e}")
            raise
    
    def query_wisdom(self, topic: str, archetype_filter: Optional[str] = None,
                    max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Query wisdom using semantic search
        
        Args:
            topic: Search query (e.g., "How to handle market crash")
            archetype_filter: Filter by persona archetype (e.g., "warren")
            max_results: Maximum number of results
        
        Returns:
            List of wisdom items with relevance scores
        """
        collection = self.collections['investor_wisdom']
        
        if collection.count() == 0:
            self.logger.warning("investor_wisdom collection is empty")
            return []
        
        try:
            # Build where filter for archetype
            where_filter = None
            if archetype_filter:
                where_filter = {"archetype": {"$contains": archetype_filter}}
            
            results = collection.query(
                query_texts=[topic],
                n_results=min(max_results, collection.count()),
                where=where_filter
            )
            
            # Format results
            wisdom_results = []
            if results['documents'] and len(results['documents'][0]) > 0:
                for i, doc in enumerate(results['documents'][0]):
                    metadata = results['metadatas'][0][i]
                    wisdom_results.append({
                        'content': doc,
                        'source': metadata.get('source', 'Unknown'),
                        'tags': metadata.get('tags', '').split(',') if metadata.get('tags') else [],
                        'archetype': metadata.get('archetype', '').split(',') if metadata.get('archetype') else [],
                        'relevance_score': round(1.0 - results['distances'][0][i], 3),
                        'confidence': metadata.get('confidence', 0.9),
                        'id': results['ids'][0][i]
                    })
            
            self.logger.info(f"✓ Found {len(wisdom_results)} wisdom items for: {topic[:50]}")
            return wisdom_results
            
        except Exception as e:
            self.logger.error(f"Failed to query wisdom: {e}")
            return []
    
    def query_strategy_performance(self, strategy_name: str, 
                                   market_condition: Optional[str] = None,
                                   max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Query historical strategy performance
        
        Args:
            strategy_name: Strategy to query
            market_condition: Optional market trend filter
            max_results: Maximum results
        
        Returns:
            List of historical performance records
        """
        collection = self.collections['strategy_performance']
        
        if collection.count() == 0:
            self.logger.warning("strategy_performance collection is empty")
            return []
        
        try:
            where_filter = {"strategy_name": strategy_name}
            if market_condition:
                where_filter["market_trend"] = market_condition
            
            results = collection.query(
                query_texts=[f"Performance of {strategy_name}"],
                n_results=min(max_results, collection.count()),
                where=where_filter
            )
            
            # Format results
            performance_results = []
            if results['documents'] and len(results['documents'][0]) > 0:
                for i, doc in enumerate(results['documents'][0]):
                    metadata = results['metadatas'][0][i]
                    performance_results.append({
                        'content': doc,
                        'strategy_name': metadata.get('strategy_name'),
                        'outcome': metadata.get('outcome'),
                        'market_trend': metadata.get('market_trend'),
                        'timestamp': metadata.get('timestamp'),
                        'id': results['ids'][0][i]
                    })
            
            return performance_results
            
        except Exception as e:
            self.logger.error(f"Failed to query strategy performance: {e}")
            return []
    
    def get_persona_context(self, persona_name: str, symbol: str, 
                           market_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get relevant knowledge context for a persona's analysis
        
        Args:
            persona_name: Persona archetype (e.g., "warren")
            symbol: Stock symbol
            market_context: Current market conditions
        
        Returns:
            Context dict with relevant wisdom and insights
        """
        # Build search query
        market_trend = market_context.get('market_trend', '')
        query = f"{symbol} investing strategy {market_trend} market"
        
        # Query wisdom for this persona
        wisdom = self.query_wisdom(
            topic=query,
            archetype_filter=persona_name,
            max_results=3
        )
        
        return {
            'persona': persona_name,
            'symbol': symbol,
            'relevant_wisdom': wisdom,
            'context_enriched': len(wisdom) > 0,
            'wisdom_count': len(wisdom)
        }
    
    async def autonomous_wisdom_ingestion(self, perplexity_service) -> Dict[str, Any]:
        """
        Autonomously fetch and ingest new market wisdom using Perplexity AI.
        
        Fetches current market regimes, legendary analyst takes, and regime-specific playbooks.
        """
        if not perplexity_service:
            return {"success": False, "error": "Perplexity service not provided"}
            
        topics = [
            "What is the current global market regime and what is the best investment playbook for it?",
            "Recent contrarian investment insights from legendary hedge fund managers",
            "Hidden risks in the current technology and AI sector according to top analysts",
            "Ancient philosophical wisdom applied to modern algorithmic trading"
        ]
        
        ingested_count = 0
        results = []
        
        for topic in topics:
            try:
                # Use Perplexity Search for real-time/deep insights
                search_data = await perplexity_service.search_financial_news(topic, max_results=3)
                
                if search_data.get('results'):
                    for news_item in search_data['results']:
                        content = f"{news_item['title']}: {news_item['summary'][:500]}"
                        source = news_item.get('source', 'Perplexity Insight')
                        
                        # Store in KB
                        doc_id = self.store_wisdom(
                            content=content,
                            source=source,
                            tags=["autonomous", "real_time_insight"],
                            archetype=["macros", "quant", "ghost"],
                            url=news_item.get('url', ''),
                            ingestion_type="autonomous"
                        )
                        ingested_count += 1
                        results.append(doc_id)
            except Exception as e:
                self.logger.error(f"Autonomous ingestion error for topic '{topic}': {e}")
                
        self.logger.info(f"🧠 Autonomous Ingestion complete. Added {ingested_count} items to memory.")
        return {
            "success": True,
            "ingested_count": ingested_count,
            "document_ids": results,
            "timestamp": datetime.now().isoformat()
        }

    def get_statistics(self) -> Dict[str, Any]:
        """Get knowledge base statistics"""
        return {
            'investor_wisdom_count': self.collections['investor_wisdom'].count(),
            'strategy_performance_count': self.collections['strategy_performance'].count(),
            'market_insights_count': self.collections['market_insights'].count(),
            'total_items': sum([
                self.collections['investor_wisdom'].count(),
                self.collections['strategy_performance'].count(),
                self.collections['market_insights'].count()
            ])
        }
    
    def reset_collection(self, collection_name: str):
        """Reset a specific collection (for testing/maintenance)"""
        if collection_name in self.collections:
            self.client.delete_collection(collection_name)
            self._initialize_collections()
            self.logger.warning(f"⚠️  Reset collection: {collection_name}")


# Global singleton instance
_knowledge_base = None


def get_knowledge_base(persist_directory: str = "./chroma_db") -> KnowledgeBaseService:
    """Get or create the global KnowledgeBaseService singleton"""
    global _knowledge_base
    if _knowledge_base is None:
        _knowledge_base = KnowledgeBaseService(persist_directory)
    return _knowledge_base
