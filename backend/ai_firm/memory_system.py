"""Firm Memory System Module

Advanced persistent memory system for the AI firm with context-aware learning,
pattern recognition, and strategic knowledge accumulation.
"""

import json
import uuid
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
import pickle
import sqlite3
import threading

class MemoryType(Enum):
    DECISION = "decision"
    PERFORMANCE = "performance"
    MARKET_EVENT = "market_event"
    AGENT_LEARNING = "agent_learning"
    STRATEGIC_INSIGHT = "strategic_insight"
    RISK_INCIDENT = "risk_incident"
    PATTERN_DISCOVERY = "pattern_discovery"

class ImportanceLevel(Enum):
    LOW = 0.3
    MEDIUM = 0.6
    HIGH = 0.8
    CRITICAL = 1.0

@dataclass
class MemoryItem:
    """Individual memory item with metadata"""
    id: str
    memory_type: MemoryType
    content: Dict[str, Any]
    importance: float
    tags: List[str]
    context_hash: str
    created_at: datetime
    last_accessed: datetime
    access_count: int
    decay_factor: float
    associated_agents: List[str]
    cross_references: List[str]

class FirmMemorySystem:
    """Advanced persistent memory system for AI firm"""
    
    def __init__(self, db_path: str = "ai_firm_memory.db"):
        self.db_path = db_path
        self.memory_cache = {}
        self.access_patterns = {}
        self.context_index = {}
        self.lock = threading.RLock()
        
        # Initialize database
        self._initialize_database()
        
        # Load recent memories into cache
        self._load_cache()
    
    def _initialize_database(self):
        """Initialize SQLite database for persistent memory storage"""
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS firm_memories (
                    id TEXT PRIMARY KEY,
                    memory_type TEXT NOT NULL,
                    content TEXT NOT NULL,
                    importance REAL NOT NULL,
                    tags TEXT NOT NULL,
                    context_hash TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    last_accessed TEXT NOT NULL,
                    access_count INTEGER DEFAULT 0,
                    decay_factor REAL DEFAULT 1.0,
                    associated_agents TEXT NOT NULL,
                    cross_references TEXT
                )
            ''')
            
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_memory_type ON firm_memories(memory_type);
                CREATE INDEX IF NOT EXISTS idx_importance ON firm_memories(importance);
                CREATE INDEX IF NOT EXISTS idx_context_hash ON firm_memories(context_hash);
                CREATE INDEX IF NOT EXISTS idx_created_at ON firm_memories(created_at);
            ''')
            
            conn.commit()
    
    def store_memory(self, memory_type: MemoryType, content: Dict[str, Any], 
                    importance: float, agents: List[str], tags: List[str] = None) -> str:
        """Store new memory item with intelligent categorization"""
        
        with self.lock:
            memory_id = str(uuid.uuid4())
            
            # Generate context hash for similarity matching
            context_hash = self._generate_context_hash(content)
            
            # Create memory item
            memory_item = MemoryItem(
                id=memory_id,
                memory_type=memory_type,
                content=content,
                importance=min(1.0, max(0.1, importance)),
                tags=tags or self._auto_generate_tags(content),
                context_hash=context_hash,
                created_at=datetime.now(),
                last_accessed=datetime.now(),
                access_count=0,
                decay_factor=1.0,
                associated_agents=agents,
                cross_references=[]
            )
            
            # Find cross-references to similar memories
            memory_item.cross_references = self._find_cross_references(memory_item)
            
            # Store in database
            self._persist_memory(memory_item)
            
            # Update cache
            self.memory_cache[memory_id] = memory_item
            
            # Update context index
            self._update_context_index(memory_item)
            
            return memory_id
    
    def recall_memories(self, context: Dict[str, Any], agent: str, 
                      memory_types: List[MemoryType] = None, 
                      limit: int = 10) -> List[MemoryItem]:
        """Recall relevant memories based on context and agent"""
        
        with self.lock:
            query_context_hash = self._generate_context_hash(context)
            
            # Get candidate memories
            candidates = self._get_candidate_memories(memory_types, agent)
            
            # Score memories by relevance
            scored_memories = []
            for memory in candidates:
                relevance_score = self._calculate_relevance_score(
                    memory, query_context_hash, context, agent
                )
                
                if relevance_score > 0.1:  # Minimum relevance threshold
                    scored_memories.append((memory, relevance_score))
            
            # Sort by relevance and importance
            scored_memories.sort(key=lambda x: x[1] * x[0].importance, reverse=True)
            
            # Return top memories and update access patterns
            top_memories = [memory for memory, score in scored_memories[:limit]]
            
            # Update access patterns
            for memory in top_memories:
                memory.last_accessed = datetime.now()
                memory.access_count += 1
                self._update_access_patterns(memory, agent)
            
            return top_memories
    
    def _generate_context_hash(self, context: Dict[str, Any]) -> str:
        """Generate hash for context similarity matching"""
        
        # Extract key features for hashing
        hash_content = {
            'market_trend': context.get('market_trend'),
            'volatility_range': self._categorize_volatility(context.get('volatility', 0.1)),
            'decision_type': context.get('decision_type'),
            'asset_class': context.get('asset_class', 'equity'),
            'time_of_day': datetime.now().hour // 6  # Quarter-day buckets
        }
        
        content_str = json.dumps(hash_content, sort_keys=True, default=str)
        return hashlib.md5(content_str.encode()).hexdigest()[:12]
    
    def _categorize_volatility(self, volatility: float) -> str:
        """Categorize volatility for context matching"""
        if volatility < 0.1:
            return 'low'
        elif volatility < 0.25:
            return 'medium'
        elif volatility < 0.4:
            return 'high'
        else:
            return 'extreme'
    
    def _auto_generate_tags(self, content: Dict[str, Any]) -> List[str]:
        """Automatically generate tags from content"""
        
        tags = []
        
        # Market condition tags
        if 'market_trend' in content:
            tags.append(f"trend_{content['market_trend']}")
        
        if 'sector' in content:
            tags.append(f"sector_{content['sector']}")
        
        # Decision tags
        if 'recommendation' in content:
            tags.append(f"action_{content['recommendation'].lower()}")
        
        # Performance tags
        if 'performance' in content:
            perf = content['performance']
            if perf > 0.8:
                tags.append('high_performance')
            elif perf < 0.4:
                tags.append('low_performance')
        
        # Risk tags
        if 'risk_score' in content:
            risk = content['risk_score']
            if risk > 0.7:
                tags.append('high_risk')
            elif risk < 0.3:
                tags.append('low_risk')
        
        return tags
    
    def _find_cross_references(self, memory_item: MemoryItem) -> List[str]:
        """Find cross-references to similar memories"""
        
        similar_memories = []
        
        # Find memories with similar context hashes
        for cached_memory in self.memory_cache.values():
            if cached_memory.id != memory_item.id:
                # Check context similarity
                if cached_memory.context_hash == memory_item.context_hash:
                    similar_memories.append(cached_memory.id)
                
                # Check tag overlap
                common_tags = set(cached_memory.tags) & set(memory_item.tags)
                if len(common_tags) >= 2:
                    similar_memories.append(cached_memory.id)
        
        return similar_memories[:5]  # Limit cross-references
    
    def _persist_memory(self, memory_item: MemoryItem):
        """Persist memory item to database"""
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO firm_memories 
                (id, memory_type, content, importance, tags, context_hash, 
                 created_at, last_accessed, access_count, decay_factor, 
                 associated_agents, cross_references)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                memory_item.id,
                memory_item.memory_type.value,
                json.dumps(memory_item.content, default=str),
                memory_item.importance,
                json.dumps(memory_item.tags),
                memory_item.context_hash,
                memory_item.created_at.isoformat(),
                memory_item.last_accessed.isoformat(),
                memory_item.access_count,
                memory_item.decay_factor,
                json.dumps(memory_item.associated_agents),
                json.dumps(memory_item.cross_references)
            ))
            conn.commit()
    
    def _load_cache(self, days_back: int = 30):
        """Load recent memories into cache for faster access"""
        
        cutoff_date = datetime.now() - timedelta(days=days_back)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute('''
                SELECT * FROM firm_memories 
                WHERE created_at > ? OR importance > 0.8
                ORDER BY importance DESC, created_at DESC
                LIMIT 1000
            ''', (cutoff_date.isoformat(),))
            
            for row in cursor:
                memory_item = MemoryItem(
                    id=row['id'],
                    memory_type=MemoryType(row['memory_type']),
                    content=json.loads(row['content']),
                    importance=row['importance'],
                    tags=json.loads(row['tags']),
                    context_hash=row['context_hash'],
                    created_at=datetime.fromisoformat(row['created_at']),
                    last_accessed=datetime.fromisoformat(row['last_accessed']),
                    access_count=row['access_count'],
                    decay_factor=row['decay_factor'],
                    associated_agents=json.loads(row['associated_agents']),
                    cross_references=json.loads(row['cross_references'] or '[]')
                )
                
                self.memory_cache[memory_item.id] = memory_item
    
    def _get_candidate_memories(self, memory_types: List[MemoryType], agent: str) -> List[MemoryItem]:
        """Get candidate memories for recall"""
        
        candidates = []
        
        for memory in self.memory_cache.values():
            # Filter by memory type if specified
            if memory_types and memory.memory_type not in memory_types:
                continue
            
            # Filter by agent relevance
            if agent not in memory.associated_agents and 'all' not in memory.associated_agents:
                continue
            
            candidates.append(memory)
        
        return candidates
    
    def _calculate_relevance_score(self, memory: MemoryItem, query_hash: str, 
                                 context: Dict[str, Any], agent: str) -> float:
        """Calculate relevance score for memory recall"""
        
        relevance_components = []
        
        # Context hash similarity (exact matches are highly relevant)
        if memory.context_hash == query_hash:
            relevance_components.append(1.0)
        else:
            # Partial hash similarity (simplified)
            similarity = len(set(memory.context_hash) & set(query_hash)) / len(set(memory.context_hash) | set(query_hash))
            relevance_components.append(similarity * 0.7)
        
        # Tag overlap
        query_tags = self._auto_generate_tags(context)
        common_tags = set(memory.tags) & set(query_tags)
        tag_relevance = len(common_tags) / max(len(memory.tags), len(query_tags), 1)
        relevance_components.append(tag_relevance * 0.8)
        
        # Agent relevance
        agent_relevance = 1.0 if agent in memory.associated_agents or 'all' in memory.associated_agents else 0.5
        relevance_components.append(agent_relevance)
        
        # Temporal relevance (recent memories more relevant, but important ones don't decay much)
        days_old = (datetime.now() - memory.created_at).days
        temporal_relevance = max(0.2, 1.0 - (days_old / 365)) * memory.decay_factor
        relevance_components.append(temporal_relevance)
        
        # Access pattern boost (frequently accessed memories are more relevant)
        access_boost = min(0.3, memory.access_count * 0.01)
        
        # Calculate weighted relevance score
        base_relevance = sum(relevance_components) / len(relevance_components)
        final_relevance = min(1.0, base_relevance + access_boost)
        
        return final_relevance * memory.importance
    
    def _update_access_patterns(self, memory: MemoryItem, agent: str):
        """Update access patterns for learning"""
        
        pattern_key = f"{agent}_{memory.memory_type.value}"
        
        if pattern_key not in self.access_patterns:
            self.access_patterns[pattern_key] = {
                'total_accesses': 0,
                'unique_memories': set(),
                'favorite_tags': {},
                'avg_importance': 0
            }
        
        pattern = self.access_patterns[pattern_key]
        pattern['total_accesses'] += 1
        pattern['unique_memories'].add(memory.id)
        
        # Update favorite tags
        for tag in memory.tags:
            pattern['favorite_tags'][tag] = pattern['favorite_tags'].get(tag, 0) + 1
        
        # Update average importance
        pattern['avg_importance'] = (
            pattern['avg_importance'] * (pattern['total_accesses'] - 1) + memory.importance
        ) / pattern['total_accesses']
    
    def _update_context_index(self, memory_item: MemoryItem):
        """Update context index for faster retrieval"""
        
        context_hash = memory_item.context_hash
        
        if context_hash not in self.context_index:
            self.context_index[context_hash] = []
        
        self.context_index[context_hash].append(memory_item.id)
        
        # Limit index size per context
        if len(self.context_index[context_hash]) > 20:
            # Remove oldest entries
            self.context_index[context_hash] = self.context_index[context_hash][-20:]
    
    def consolidate_memories(self, days_threshold: int = 30) -> Dict[str, Any]:
        """Consolidate old memories to prevent memory bloat"""
        
        cutoff_date = datetime.now() - timedelta(days=days_threshold)
        
        consolidation_stats = {
            'memories_before': len(self.memory_cache),
            'memories_consolidated': 0,
            'memories_deleted': 0,
            'space_saved_mb': 0
        }
        
        with self.lock:
            # Get old memories
            old_memories = [
                memory for memory in self.memory_cache.values()
                if memory.created_at < cutoff_date and memory.importance < 0.7
            ]
            
            # Group similar memories for consolidation
            context_groups = {}
            for memory in old_memories:
                if memory.context_hash not in context_groups:
                    context_groups[memory.context_hash] = []
                context_groups[memory.context_hash].append(memory)
            
            # Consolidate groups with multiple memories
            for context_hash, memory_group in context_groups.items():
                if len(memory_group) > 3:
                    consolidated_memory = self._consolidate_memory_group(memory_group)
                    
                    # Remove old memories
                    for old_memory in memory_group:
                        if old_memory.id in self.memory_cache:
                            del self.memory_cache[old_memory.id]
                            consolidation_stats['memories_deleted'] += 1
                    
                    # Add consolidated memory
                    self.memory_cache[consolidated_memory.id] = consolidated_memory
                    consolidation_stats['memories_consolidated'] += 1
            
            # Update database
            self._sync_cache_to_database()
            
            consolidation_stats['memories_after'] = len(self.memory_cache)
        
        return consolidation_stats
    
    def _consolidate_memory_group(self, memory_group: List[MemoryItem]) -> MemoryItem:
        """Consolidate a group of similar memories into one"""
        
        # Use the most important memory as base
        base_memory = max(memory_group, key=lambda m: m.importance)
        
        # Combine content
        consolidated_content = {
            'type': 'consolidated_memory',
            'original_count': len(memory_group),
            'combined_insights': [m.content for m in memory_group],
            'importance_distribution': [m.importance for m in memory_group],
            'access_patterns': [m.access_count for m in memory_group]
        }
        
        # Combine tags and agents
        all_tags = set()
        all_agents = set()
        
        for memory in memory_group:
            all_tags.update(memory.tags)
            all_agents.update(memory.associated_agents)
        
        # Create consolidated memory
        consolidated_memory = MemoryItem(
            id=str(uuid.uuid4()),
            memory_type=base_memory.memory_type,
            content=consolidated_content,
            importance=max(m.importance for m in memory_group),
            tags=list(all_tags),
            context_hash=base_memory.context_hash,
            created_at=min(m.created_at for m in memory_group),
            last_accessed=max(m.last_accessed for m in memory_group),
            access_count=sum(m.access_count for m in memory_group),
            decay_factor=max(m.decay_factor for m in memory_group),
            associated_agents=list(all_agents),
            cross_references=[]
        )
        
        return consolidated_memory
    
    def _sync_cache_to_database(self):
        """Sync memory cache back to database"""
        
        with sqlite3.connect(self.db_path) as conn:
            # Clear database
            conn.execute('DELETE FROM firm_memories')
            
            # Reinsert all cached memories
            for memory in self.memory_cache.values():
                conn.execute('''
                    INSERT INTO firm_memories 
                    (id, memory_type, content, importance, tags, context_hash, 
                     created_at, last_accessed, access_count, decay_factor, 
                     associated_agents, cross_references)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    memory.id,
                    memory.memory_type.value,
                    json.dumps(memory.content, default=str),
                    memory.importance,
                    json.dumps(memory.tags),
                    memory.context_hash,
                    memory.created_at.isoformat(),
                    memory.last_accessed.isoformat(),
                    memory.access_count,
                    memory.decay_factor,
                    json.dumps(memory.associated_agents),
                    json.dumps(memory.cross_references)
                ))
            
            conn.commit()
    
    def get_memory_analytics(self) -> Dict[str, Any]:
        """Get comprehensive memory system analytics"""
        
        with self.lock:
            total_memories = len(self.memory_cache)
            
            if total_memories == 0:
                return {'total_memories': 0, 'memory_types': {}, 'agents': {}}
            
            # Memory type distribution
            type_distribution = {}
            for memory in self.memory_cache.values():
                type_key = memory.memory_type.value
                type_distribution[type_key] = type_distribution.get(type_key, 0) + 1
            
            # Agent memory distribution
            agent_distribution = {}
            for memory in self.memory_cache.values():
                for agent in memory.associated_agents:
                    agent_distribution[agent] = agent_distribution.get(agent, 0) + 1
            
            # Importance distribution
            importance_levels = {'low': 0, 'medium': 0, 'high': 0, 'critical': 0}
            for memory in self.memory_cache.values():
                if memory.importance < 0.4:
                    importance_levels['low'] += 1
                elif memory.importance < 0.7:
                    importance_levels['medium'] += 1
                elif memory.importance < 0.9:
                    importance_levels['high'] += 1
                else:
                    importance_levels['critical'] += 1
            
            # Access patterns
            avg_access_count = sum(m.access_count for m in self.memory_cache.values()) / total_memories
            
            return {
                'total_memories': total_memories,
                'memory_types': type_distribution,
                'agent_memories': agent_distribution,
                'importance_distribution': importance_levels,
                'access_analytics': {
                    'average_access_count': round(avg_access_count, 2),
                    'most_accessed_memory': max(self.memory_cache.values(), key=lambda m: m.access_count).id,
                    'access_patterns': len(self.access_patterns)
                },
                'system_health': {
                    'cache_size_mb': self._estimate_cache_size(),
                    'database_size_mb': self._estimate_database_size(),
                    'fragmentation_level': 'low'
                },
                'last_consolidation': datetime.now().isoformat()
            }
    
    def _estimate_cache_size(self) -> float:
        """Estimate memory cache size in MB"""
        
        total_size = 0
        for memory in self.memory_cache.values():
            # Rough estimation
            content_size = len(json.dumps(memory.content, default=str))
            total_size += content_size + 500  # Add overhead
        
        return round(total_size / (1024 * 1024), 2)
    
    def _estimate_database_size(self) -> float:
        """Estimate database size in MB"""
        
        try:
            import os
            size_bytes = os.path.getsize(self.db_path)
            return round(size_bytes / (1024 * 1024), 2)
        except:
            return 0.5  # Default estimate
