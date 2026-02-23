"""Institutional Knowledge Base (Quantum Memory)

Powered by ChromaDB for semantic retrieval of investment lore and institutional wisdom.
"""

import os
import logging
import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class KnowledgeBase:
    """Institutional Knowledge Base using ChromaDB"""
    
    def __init__(self, persist_dir: str = "chroma_db"):
        self.persist_dir = persist_dir
        self.client = chromadb.PersistentClient(path=self.persist_dir)
        self.collection = self.client.get_or_create_collection(name="institutional_wisdom")
        
        # Seed if empty
        if self.collection.count() == 0:
            self._seed_wisdom()
            
        logger.info(f"🧠 Knowledge Base active. Items: {self.collection.count()}")

    def _seed_wisdom(self):
        """Seed the KB with foundational investment lore"""
        wisdom = [
             {
                "id": "buffett_1",
                "text": "Rule No. 1: Never lose money. Rule No. 2: Never forget rule No. 1.",
                "metadata": {"source": "Warren Buffett", "category": "Survival"}
            },
            {
                "id": "buffett_2",
                "text": "Be fearful when others are greedy and greedy when others are fearful.",
                "metadata": {"source": "Warren Buffett", "category": "Sentiment"}
            },
            {
                "id": "dalio_1",
                "text": "If you don't own gold, you know neither history nor economics.",
                "metadata": {"source": "Ray Dalio", "category": "Macro"}
            },
            {
                "id": "dalio_2",
                "text": "Pain + Reflection = Progress.",
                "metadata": {"source": "Ray Dalio", "category": "Mindset"}
            },
            {
                "id": "munger_1",
                "text": "The big money is not in the buying and the selling, but in the waiting.",
                "metadata": {"source": "Charlie Munger", "category": "Patience"}
            },
            {
                "id": "ghos_1",
                "text": "The market is a mirror of collective emotion. It does not think, it feels.",
                "metadata": {"source": "The Ghost", "category": "Quantum Meta"}
            },
            {
                "id": "hindi_1",
                "text": "Chalti ka naam gaadi (Only that which moves is a car/working). Momentum is king.",
                "metadata": {"source": "Hindi Wisdom", "category": "Momentum"}
            },
            {
                "id": "hindi_2",
                "text": "Boond boond se ghada bharta hai (Drop by drop the pot fills). Consistent small gains.",
                "metadata": {"source": "Hindi Wisdom", "category": "Compounding"}
            }
        ]
        
        self.collection.add(
            documents=[item["text"] for item in wisdom],
            metadatas=[item["metadata"] for item in wisdom],
            ids=[item["id"] for item in wisdom]
        )
        logger.info(f"🌱 Seeded Institutional Knowledge Base with {len(wisdom)} core principles.")

    def query_wisdom(self, query: str, n_results: int = 2) -> List[Dict[str, Any]]:
        """Find relevant wisdom for a given market scenario"""
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results
            )
            
            output = []
            for i in range(len(results['documents'][0])):
                output.append({
                    'text': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'distance': results['distances'][0][i] if 'distances' in results else 0
                })
            return output
        except Exception as e:
            logger.error(f"KB Query failed: {e}")
            return []

# Singleton
_kb = None

def get_knowledge_base():
    global _kb
    if _kb is None:
        _kb = KnowledgeBase()
    return _kb
