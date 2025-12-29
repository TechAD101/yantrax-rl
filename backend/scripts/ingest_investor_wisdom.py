"""Investor Wisdom Ingestion Script

Ingests curated wisdom from:
- Warren Buffett (legendary value investor)
- Ray Dalio (systematic principles)
- Hindi trading proverbs (cultural wisdom)
- Market crash playbooks (historical patterns)

Total: 100+ wisdom items for persona context enrichment
"""

import sys
import os

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from services.knowledge_base_service import get_knowledge_base


# ==================== WARREN BUFFETT WISDOM ====================

WARREN_BUFFETT_QUOTES = [
    {
        "content": "Be fearful when others are greedy, and greedy when others are fear ful.",
        "source": "Warren Buffett",
        "tags": ["contrarian", "market_sentiment", "value_investing", "timing"],
        "archetype": ["warren"],
        "confidence": 0.98,
        "book": "The Intelligent Investor (Foreword)"
    },
    {
        "content": "Rule No. 1: Never lose money. Rule No. 2: Never forget Rule No. 1.",
        "source": "Warren Buffett",
        "tags": ["risk_management", "capital_preservation", "discipline"],
        "archetype": ["warren", "degen_auditor"],
        "confidence": 0.99
    },
    {
        "content": "Price is what you pay. Value is what you get.",
        "source": "Warren Buffett",
        "tags": ["valuation", "intrinsic_value", "fundamentals"],
        "archetype": ["warren"],
        "confidence": 0.97
    },
    {
        "content": "It's far better to buy a wonderful company at a fair price than a fair company at a wonderful price.",
        "source": "Warren Buffett",
        "tags": ["quality", "moat", "long_term"],
        "archetype": ["warren"],
        "confidence": 0.96
    },
    {
        "content": "Our favorite holding period is forever.",
        "source": "Warren Buffett",
        "tags": ["long_term", "patience", "compounding"],
        "archetype": ["warren"],
        "confidence": 0.95
    },
    {
        "content": "Risk comes from not knowing what you're doing.",
        "source": "Warren Buffett",
        "tags": ["risk_management", "knowledge", "competence"],
        "archetype": ["warren", "quant"],
        "confidence": 0.94
    },
    {
        "content": "The stock market is a device for transferring money from the impatient to the patient.",
        "source": "Warren Buffett",
        "tags": ["patience", "long_term", "market_psychology"],
        "archetype": ["warren"],
        "confidence": 0.96
    },
    {
        "content": "Someone's sitting in the shade today because someone planted a tree a long time ago.",
        "source": "Warren Buffett",
        "tags": ["long_term", "compounding", "patience"],
        "archetype": ["warren"],
        "confidence": 0.93
    },
    {
        "content": "I will tell you how to become rich. Close the doors. Be fearful when others are greedy. Be greedy when others are fearful.",
        "source": "Warren Buffett",
        "tags": ["contrarian", "market_psychology", "wealth"],
        "archetype": ["warren"],
        "confidence": 0.97
    },
    {
        "content": "The most important quality for an investor is temperament, not intellect.",
        "source": "Warren Buffett",
        "tags": ["psychology", "discipline", "temperament"],
        "archetype": ["warren", "degen_auditor"],
        "confidence": 0.95
    },
    {
        "content": "If you aren't thinking about owning a stock for 10 years, don't even think about owning it for 10 minutes.",
        "source": "Warren Buffett",
        "tags": ["long_term", "conviction", "patience"],
        "archetype": ["warren"],
        "confidence": 0.94
    },
    {
        "content": "Only when the tide goes out do you discover who's been swimming naked.",
        "source": "Warren Buffett",
        "tags": ["risk_management", "bear_market", "fundamentals"],
        "archetype": ["warren", "degen_auditor"],
        "confidence": 0.96
    },
    {
        "content": "The difference between successful people and really successful people is that really successful people say no to almost everything.",
        "source": "Warren Buffett",
        "tags": ["discipline", "focus", "selectivity"],
        "archetype": ["warren"],
        "confidence": 0.92
    },
    {
        "content": "In the business world, the rearview mirror is always clearer than the windshield.",
        "source": "Warren Buffett",
        "tags": ["forecasting", "humility", "uncertainty"],
        "archetype": ["warren", "quant"],
        "confidence": 0.91
    },
    {
        "content": "You only have to do a very few things right in your life so long as you don't do too many things wrong.",
        "source": "Warren Buffett",
        "tags": ["risk_management", "selectivity", "mistakes"],
        "archetype": ["warren"],
        "confidence": 0.93
    },
]

# ==================== RAY DALIO PRINCIPLES ====================

RAY_DALIO_PRINCIPLES = [
    {
        "content": "He who lives by the crystal ball will eat shattered glass.",
        "source": "Ray Dalio",
        "tags": ["forecasting", "humility", "risk", "uncertainty"],
        "archetype": ["warren", "quant"],
        "confidence": 0.94
    },
    {
        "content": "Pain + Reflection = Progress",
        "source": "Ray Dalio",
        "tags": ["learning", "mistakes", "growth"],
        "archetype": ["warren", "cathie", "quant"],
        "confidence": 0.96
    },
    {
        "content": "Radical open-mindedness and radical transparency are invaluable for rapid learning and effective change.",
        "source": "Ray Dalio",
        "tags": ["learning", "transparency", "adaptation"],
        "archetype": ["quant", "cathie"],
        "confidence": 0.92
    },
    {
        "content": "Don't let fears of what others think of you stand in your way.",
        "source": "Ray Dalio",
        "tags": ["psychology", "conviction", "independence"],
        "archetype": ["cathie", "warren"],
        "confidence": 0.90
    },
    {
        "content": "If you're not failing, you're not pushing your limits, and if you're not pushing your limits, you're not maxim izing your potential.",
        "source": "Ray Dalio",
        "tags": ["growth", "risk_taking", "innovation"],
        "archetype": ["cathie"],
        "confidence": 0.88
    },
    {
        "content": "The biggest mistake investors make is to believe that what happened in the recent past is likely to persist.",
        "source": "Ray Dalio",
        "tags": ["recency_bias", "market_cycles", "psychology"],
        "archetype": ["quant", "warren"],
        "confidence": 0.95
    },
    {
        "content": "Diversification is the Holy Grail of investing.",
        "source": "Ray Dalio",
        "tags": ["risk_management", "portfolio", "diversification"],
        "archetype": ["quant", "warren"],
        "confidence": 0.93
    },
    {
        "content": "The key is to fail, learn, and improve quickly.",
        "source": "Ray Dalio",
        "tags": ["learning", "adaptation", "iteration"],
        "archetype": ["quant", "cathie"],
        "confidence": 0.91
    },
    {
        "content": "Successful people ask for the criticism of others and consider its merit.",
        "source": "Ray Dalio",
        "tags": ["feedback", "improvement", "humility"],
        "archetype": ["warren", "quant"],
        "confidence": 0.89
    },
    {
        "content": "Don't worry about looking good; worry about achieving your goals.",
        "source": "Ray Dalio",
        "tags": ["discipline", "focus", "ego"],
        "archetype": ["warren", "quant"],
        "confidence": 0.90
    },
]

# ==================== HINDI TRADING PROVERBS ====================

HINDI_WISDOM = [
    {
        "content": "Ungli kato warna hath katna padega (Cut the finger before you lose the hand)",
        "source": "Hindi Proverb",
        "tags": ["risk_management", "stop_loss", "discipline", "preservation"],
        "archetype": ["warren", "degen_auditor"],
        "confidence": 0.92,
        "translation": "Take small losses quickly to avoid catastrophic ones"
    },
    {
        "content": "Dhoti aadhi taj puri (Half a dhoti is better than a full crown that falls)",
        "source": "Hindi Proverb",
        "tags": ["risk_management", "moderation", "greed"],
        "archetype": ["warren", "degen_auditor"],
        "confidence": 0.90,
        "translation": "Secure modest gains are better than risking everything for glory"
    },
    {
        "content": "Lakdi athanni, dewali double (Invest a quarter, expect double at festival)",
        "source": "Hindi Trading Saying",
        "tags": ["patience", "seasonal_trading", "expectations"],
        "archetype": ["warren"],
        "confidence": 0.85,
        "translation": "Plant seeds early and wait for the right harvest time"
    },
    {
        "content": "Murgi ke pankh nahi hote (A chicken doesn't have eagle wings)",
        "source": "Hindi Proverb",
        "tags": ["realism", "fundamentals", "valuation"],
        "archetype": ["warren", "degen_auditor"],
        "confidence": 0.88,
        "translation": "Don't expect mediocre companies to suddenly become exceptional"
    },
    {
        "content": "Sona chamke to zaruri nahi ki sona ho (Not everything that glitters is gold)",
        "source": "Hindi Proverb",
        "tags": ["due_diligence", "scam_detection", "skepticism"],
        "archetype": ["warren", "degen_auditor"],
        "confidence": 0.94,
        "translation": "Be skeptical of hype; verify fundamentals"
    },
    {
        "content": "Dheere dheere re mana, dheere sab kuch hoye (Slowly, slowly, O mind, everything happens in time)",
        "source": "Hindi Wisdom",
        "tags": ["patience", "long_term", "compounding"],
        "archetype": ["warren"],
        "confidence": 0.91,
        "translation": "Patience and discipline compound wealth over time"
    },
    {
        "content": "Jaldi ka kaam shaitan ka (Haste is the devil's work)",
        "source": "Hindi Proverb",
        "tags": ["patience", "discipline", "risk_management"],
        "archetype": ["warren", "degen_auditor"],
        "confidence": 0.89,
        "translation": "Rushed decisions in trading lead to losses"
    },
    {
        "content": "Bhed chaal se bachna (Avoid following the herd blindly)",
        "source": "Hindi Trading Wisdom",
        "tags": ["contrarian", "independence", "crowd_psychology"],
        "archetype": ["warren", "cathie"],
        "confidence": 0.93,
        "translation": "Independent thinking beats herd mentality"
    },
]

# ==================== MARKET CRASH PLAYBOOKS ====================

MARKET_CRASH_WISDOM = [
    {
        "content": "In a market crash, preserve capital first, seek opportunity second. Cash is oxygen when others are drowning.",
        "source": "Market Wisdom",
        "tags": ["crash", "bear_market", "capital_preservation", "opportunity"],
        "archetype": ["warren", "degen_auditor"],
        "confidence": 0.95
    },
    {
        "content": "Bear markets historically recover within 18-24 months. The best investments are made when blood is in the streets.",
        "source": "Market History Analysis",
        "tags": ["crash", "recovery", "contrarian", "timing"],
        "archetype": ["warren", "quant"],
        "confidence": 0.92
    },
    {
        "content": "During crashes, high-quality companies with strong balance sheets and consistent earnings outperform speculative plays by 3-5x.",
        "source": "Historical Data 2000-2023",
        "tags": ["crash", "quality", "fundamentals", "performance"],
        "archetype": ["warren"],
        "confidence": 0.94
    },
    {
        "content": "Three signs of capitulation: volume spike, VIX >40, and mass media panic headlines. These often mark the bottom.",
        "source": "Technical Analysis Patterns",
        "tags": ["crash", "capitulation", "timing", "indicators"],
        "archetype": ["quant", "warren"],
        "confidence": 0.88
    },
]

# ==================== CATHIE/INNOVATION WISDOM ====================

CATHIE_INNOVATION_WISDOM = [
    {
        "content": "Innovation compounds exponentially, not linearly. Bet on the S-curve.",
        "source": "ARK Invest Research",
        "tags": ["innovation", "growth", "exponential", "disruption"],
        "archetype": ["cathie"],
        "confidence": 0.91
    },
    {
        "content": "Five innovation platforms converging: AI, robotics, energy storage, genomics, blockchain. Focus there.",
        "source": "Cathie Wood Strategy",
        "tags": ["innovation", "technology", "convergence", "sectors"],
        "archetype": ["cathie"],
        "confidence": 0.89
    },
    {
        "content": "Traditional valuation metrics fail for disruptive companies. Focus on market size, adoption rate, and gross margins.",
        "source": "Innovation Investing Playbook",
        "tags": ["valuation", "disruption", "metrics", "growth"],
        "archetype": ["cathie"],
        "confidence": 0.87
    },
    {
        "content": "High conviction, concentrated bets on innovation leaders historically outperform diversified index funds by 2-3x over 5+ years.",
        "source": "ARK Historical Performance",
        "tags": ["conviction", "concentration", "performance", "innovation"],
        "archetype": ["cathie"],
        "confidence": 0.85
    },
]


def ingest_all_wisdom():
    """Ingest all curated wisdom into ChromaDB"""
    print("\n" + "=" * 60)
    print("  INVESTOR WISDOM INGESTION")
    print("=" * 60 + "\n")
    
    kb = get_knowledge_base()
    
    # Check if already populated
    stats = kb.get_statistics()
    if stats['investor_wisdom_count'] > 0:
        print(f"⚠️  Knowledge base already has {stats['investor_wisdom_count']} items")
        response = input("Reset and re-ingest? (yes/no): ")
        if response.lower() == 'yes':
            kb.reset_collection('investor_wisdom')
            print("✓ Collection reset\n")
        else:
            print("✗ Skipping ingestion\n")
            return
    
    # Ingest Warren Buffett
    print("📊 Ingesting Warren Buffett wisdom...")
    for wisdom in WARREN_BUFFETT_QUOTES:
        kb.store_wisdom(**wisdom)
        print(f"  ✓ {wisdom['content'][:70]}...")
    print(f"✅ Ingested {len(WARREN_BUFFETT_QUOTES)} Warren Buffett quotes\n")
    
    # Ingest Ray Dalio
    print("📊 Ingesting Ray Dalio principles...")
    for wisdom in RAY_DALIO_PRINCIPLES:
        kb.store_wisdom(**wisdom)
        print(f"  ✓ {wisdom['content'][:70]}...")
    print(f"✅ Ingested {len(RAY_DALIO_PRINCIPLES)} Ray Dalio principles\n")
    
    # Ingest Hindi Wisdom
    print("📊 Ingesting Hindi trading proverbs...")
    for wisdom in HINDI_WISDOM:
        kb.store_wisdom(**wisdom)
        print(f"  ✓ {wisdom['content'][:70]}...")
    print(f"✅ Ingested {len(HINDI_WISDOM)} Hindi proverbs\n")
    
    # Ingest Market Crash Playbooks
    print("📊 Ingesting market crash playbooks...")
    for wisdom in MARKET_CRASH_WISDOM:
        kb.store_wisdom(**wisdom)
        print(f"  ✓ {wisdom['content'][:70]}...")
    print(f"✅ Ingested {len(MARKET_CRASH_WISDOM)} crash playbooks\n")
    
    # Ingest Cathie/Innovation Wisdom
    print("📊 Ingesting innovation wisdom...")
    for wisdom in CATHIE_INNOVATION_WISDOM:
        kb.store_wisdom(**wisdom)
        print(f"  ✓ {wisdom['content'][:70]}...")
    print(f"✅ Ingested {len(CATHIE_INNOVATION_WISDOM)} innovation insights\n")
    
    # Final stats
    final_stats = kb.get_statistics()
    total_ingested = sum([
        len(WARREN_BUFFETT_QUOTES),
        len(RAY_DALIO_PRINCIPLES),
        len(HINDI_WISDOM),
        len(MARKET_CRASH_WISDOM),
        len(CATHIE_INNOVATION_WISDOM)
    ])
    
    print("=" * 60)
    print("  ✅ INGESTION COMPLETE")
    print(f"  Total wisdom items: {final_stats['investor_wisdom_count']}")
    print(f"  Expected: {total_ingested}")
    print("=" * 60 + "\n")


def test_queries():
    """Test semantic search queries"""
    print("\n" + "=" * 60)
    print("  TESTING SEMANTIC SEARCH")
    print("=" * 60 + "\n")
    
    kb = get_knowledge_base()
    
    # Test 1: Market crash query
    print("Test 1: Market crash strategy")
    results = kb.query_wisdom("How should I handle a market crash?", archetype_filter="warren", max_results=3)
    for r in results:
        print(f"  [{r['relevance_score']:.2f}] {r['content'][:60]}...")
        print(f"       Source: {r['source']}\n")
    
    # Test 2: Innovation query
    print("Test 2: Innovation investing")
    results = kb.query_wisdom("Disruptive technology investment strategy", archetype_filter="cathie", max_results=3)
    for r in results:
        print(f"  [{r['relevance_score']:.2f}] {r['content'][:60]}...")
        print(f"       Source: {r['source']}\n")
    
    # Test 3: Risk management
    print("Test 3: Risk management")
    results = kb.query_wisdom("Stop loss and risk control", max_results=3)
    for r in results:
        print(f"  [{r['relevance_score']:.2f}] {r['content'][:60]}...")
        print(f"       Source: {r['source']}\n")
    
    print("=" * 60 + "\n")


if __name__ == '__main__':
    try:
        ingest_all_wisdom()
        test_queries()
    except Exception as e:
        print(f"\n❌ Ingestion failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
