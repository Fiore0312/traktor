#!/usr/bin/env python3
"""
Persistent Memory System for LangChain Agents
==============================================

Provides persistent memory for DJ agents that learns from past decisions
and improves performance over time.

Features:
- Persistent ConversationBufferMemory with ChromaDB backend
- Knowledge base storing successful DJ decisions
- Session-based memory management
- Load/save functionality for training data

Author: DJ Fiore AI System
Version: 1.0
Created: 2025-10-13
"""

import os
import json
import sqlite3
import pickle
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from pathlib import Path

try:
    # Try new imports first (langchain >= 0.1.0)
    from langchain_chroma import Chroma
except ImportError:
    # Fallback to old imports
    from langchain_community.vectorstores import Chroma

from langchain_community.embeddings import FakeEmbeddings
from langchain.docstore.document import Document
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from dotenv import load_dotenv

load_dotenv()

class PersistentMemorySystem:
    """
    Persistent memory system for DJ agents that learns from past decisions.

    Uses ChromaDB for vector storage and SQLite for structured data.
    """

    def __init__(self, memory_dir: str = "C:/djfiore/data/memory"):
        """
        Initialize persistent memory system.

        Args:
            memory_dir: Directory for memory storage
        """
        self.memory_dir = Path(memory_dir)
        self.memory_dir.mkdir(exist_ok=True)

        # Initialize vector store for semantic memory (optional - fallback to JSON if chromadb unavailable)
        try:
            # Use FakeEmbeddings for local operation (no API key required)
            self.embeddings = FakeEmbeddings(size=384)

            # Initialize ChromaDB vector store
            self.vector_store = Chroma(
                persist_directory=str(self.memory_dir / "chroma_db"),
                embedding_function=self.embeddings
            )
            print("[OK] ChromaDB vector store initialized (using local embeddings)")
        except (ImportError, Exception) as e:
            print(f"[WARN] ChromaDB not available ({e}), using JSON-only memory")
            self.vector_store = None
            self.embeddings = None

        # Initialize conversation history storage (list of messages)
        self.conversation_history = []

        # Load existing memories
        self._load_memories()

    def _load_memories(self) -> None:
        """Load existing memories from storage."""
        # Load conversation history
        conv_file = self.memory_dir / "conversation_history.json"
        if conv_file.exists():
            try:
                with open(conv_file, 'r', encoding='utf-8') as f:
                    history_data = json.load(f)

                # Restore conversation history (limit to last 100 messages)
                if 'messages' in history_data:
                    messages = history_data['messages']
                    # Keep only last 100 messages to prevent overflow
                    recent_messages = messages[-100:] if len(messages) > 100 else messages

                    for msg_data in recent_messages:
                        if msg_data['type'] == 'human':
                            self.conversation_history.append(HumanMessage(content=msg_data['content']))
                        elif msg_data['type'] == 'ai':
                            self.conversation_history.append(AIMessage(content=msg_data['content']))

            except Exception as e:
                print(f"[INFO] No previous conversation history found (first run)")

        # Load knowledge base
        self._load_knowledge_base()

    def _load_knowledge_base(self) -> None:
        """Load knowledge base with successful DJ decisions."""
        knowledge_file = self.memory_dir / "knowledge_base.json"
        if knowledge_file.exists():
            try:
                with open(knowledge_file, 'r', encoding='utf-8') as f:
                    knowledge_data = json.load(f)

                # Store in vector DB
                documents = []
                for entry in knowledge_data.get('entries', []):
                    # Get metadata with safe defaults
                    entry_meta = entry.get('metadata', {})
                    doc = Document(
                        page_content=entry['content'],
                        metadata={
                            'decision_type': entry.get('decision_type', 'unknown'),
                            'genre': entry_meta.get('genre', 'unknown'),
                            'energy_level': entry_meta.get('energy_level', 'unknown'),
                            'bpm_range': entry_meta.get('bpm_range', 'unknown'),
                            'success_score': entry.get('success_score', 1.0),
                            'timestamp': entry.get('timestamp', datetime.now().isoformat()),
                            'reasoning': entry_meta.get('reasoning', '')
                        }
                    )
                    documents.append(doc)

                if documents and self.vector_store:
                    # Add to vector store (if available)
                    self.vector_store.add_documents(documents)

            except Exception as e:
                print(f"[INFO] No previous knowledge base found (first run)")

    def save_conversation(self) -> None:
        """Save current conversation history to disk."""
        conv_file = self.memory_dir / "conversation_history.json"

        # Prune conversation history to last 100 messages before saving
        if len(self.conversation_history) > 100:
            self.conversation_history = self.conversation_history[-100:]

        # Extract messages from conversation history
        messages = []
        for msg in self.conversation_history:
            if isinstance(msg, HumanMessage):
                messages.append({
                    'type': 'human',
                    'content': msg.content
                })
            elif isinstance(msg, AIMessage):
                messages.append({
                    'type': 'ai',
                    'content': msg.content
                })

        # Save to file
        conv_data = {
            'timestamp': datetime.now().isoformat(),
            'messages': messages,
            'total_messages': len(messages)
        }

        with open(conv_file, 'w', encoding='utf-8') as f:
            json.dump(conv_data, f, indent=2, ensure_ascii=False)

    def add_knowledge_entry(self, decision_type: str, content: str, metadata: Dict[str, Any],
                          success_score: float = 1.0) -> None:
        """
        Add a successful decision to the knowledge base.

        Args:
            decision_type: Type of decision (e.g., 'track_selection', 'transition', 'energy_flow')
            content: Description of the decision and reasoning
            metadata: Additional metadata about the decision
            success_score: How successful was this decision (0.0-1.0)
        """
        # Create document for vector store
        doc = Document(
            page_content=content,
            metadata={
                'decision_type': decision_type,
                'genre': metadata.get('genre', 'unknown'),
                'energy_level': metadata.get('energy_level', 'unknown'),
                'bpm_range': metadata.get('bpm_range', 'unknown'),
                'success_score': success_score,
                'timestamp': datetime.now().isoformat(),
                'reasoning': metadata.get('reasoning', '')
            }
        )

        # Add to vector store (if available)
        if self.vector_store:
            self.vector_store.add_documents([doc])

        # Save to knowledge base JSON
        knowledge_file = self.memory_dir / "knowledge_base.json"

        # Load existing knowledge
        try:
            with open(knowledge_file, 'r', encoding='utf-8') as f:
                knowledge_data = json.load(f)
        except FileNotFoundError:
            knowledge_data = {'entries': []}

        # Add new entry
        entry = {
            'decision_type': decision_type,
            'content': content,
            'metadata': metadata,
            'success_score': success_score,
            'timestamp': datetime.now().isoformat()
        }

        knowledge_data['entries'].append(entry)

        # Keep only last 1000 entries
        if len(knowledge_data['entries']) > 1000:
            knowledge_data['entries'] = knowledge_data['entries'][-1000:]

        # Save back to file
        with open(knowledge_file, 'w', encoding='utf-8') as f:
            json.dump(knowledge_data, f, indent=2, ensure_ascii=False)

    def query_knowledge(self, query: str, decision_type: Optional[str] = None,
                       genre: Optional[str] = None, limit: int = 5) -> List[Document]:
        """
        Query the knowledge base for similar past decisions.

        Args:
            query: Query text to search for
            decision_type: Filter by decision type (optional)
            genre: Filter by genre (optional)
            limit: Maximum number of results to return

        Returns:
            List of relevant documents with similar past decisions
        """
        # Search vector store (if available)
        if self.vector_store:
            # Build filter
            filter_dict = {}
            if decision_type:
                filter_dict['decision_type'] = decision_type
            if genre:
                filter_dict['genre'] = genre

            # Search vector store
            results = self.vector_store.similarity_search(
                query=query,
                k=limit,
                filter=filter_dict if filter_dict else None
            )

            return results
        else:
            # Fallback to JSON-based search (simple keyword matching)
            knowledge_file = self.memory_dir / "knowledge_base.json"
            if not knowledge_file.exists():
                return []

            try:
                with open(knowledge_file, 'r', encoding='utf-8') as f:
                    knowledge_data = json.load(f)

                # Simple keyword matching
                query_lower = query.lower()
                matches = []
                for entry in knowledge_data.get('entries', []):
                    content_lower = entry['content'].lower()
                    if query_lower in content_lower or any(word in content_lower for word in query_lower.split()):
                        doc = Document(
                            page_content=entry['content'],
                            metadata=entry.get('metadata', {})
                        )
                        matches.append(doc)

                # Return top matches
                return matches[:limit]
            except Exception as e:
                print(f"Error in fallback query: {e}")
                return []

    def get_conversation_context(self, max_messages: int = 20, as_string: bool = False):
        """
        Get recent conversation context.

        Args:
            max_messages: Maximum number of messages to return
            as_string: If True, return formatted string; if False, return list of dicts

        Returns:
            List of message dicts or formatted string
        """
        # Get recent messages
        messages = self.conversation_history
        recent_messages = messages[-max_messages:] if len(messages) > max_messages else messages

        if as_string:
            # Format for LLM prompt
            context = ""
            for msg in recent_messages:
                if isinstance(msg, HumanMessage):
                    context += f"Human: {msg.content}\n"
                elif isinstance(msg, AIMessage):
                    context += f"AI: {msg.content}\n"
            return context
        else:
            # Return as list of dicts for programmatic access
            context_list = []
            for msg in recent_messages:
                if isinstance(msg, HumanMessage):
                    context_list.append({'type': 'human', 'content': msg.content})
                elif isinstance(msg, AIMessage):
                    context_list.append({'type': 'ai', 'content': msg.content})
            return context_list

    def clear_session_memory(self) -> None:
        """Clear current session's conversation memory but keep knowledge base."""
        self.conversation_history = []
        print("[OK] Session memory cleared. Knowledge base preserved.")

    def get_memory_stats(self) -> Dict[str, Any]:
        """Get statistics about the memory system."""
        # Count knowledge entries from JSON file
        knowledge_count = 0
        try:
            knowledge_file = self.memory_dir / "knowledge_base.json"
            if knowledge_file.exists():
                with open(knowledge_file, 'r', encoding='utf-8') as f:
                    knowledge_data = json.load(f)
                    knowledge_count = len(knowledge_data.get('entries', []))
        except Exception:
            pass

        return {
            'conversation_messages': len(self.conversation_history),
            'knowledge_entries': knowledge_count,
            'vector_store_enabled': self.vector_store is not None,
            'memory_directory': str(self.memory_dir),
            'last_save': datetime.now().isoformat()
        }

# Global memory system instance
_memory_system = None

def get_memory_system() -> PersistentMemorySystem:
    """Get or create the global memory system instance."""
    global _memory_system
    if _memory_system is None:
        _memory_system = PersistentMemorySystem()
    return _memory_system

def save_current_session() -> None:
    """Save the current session state."""
    memory_system = get_memory_system()
    memory_system.save_conversation()

def add_knowledge(decision_type: str, content: str, metadata: Dict[str, Any],
                 success_score: float = 1.0) -> None:
    """Add a knowledge entry to the persistent memory."""
    memory_system = get_memory_system()
    memory_system.add_knowledge_entry(decision_type, content, metadata, success_score)

def query_knowledge_base(query: str, **kwargs) -> List[Document]:
    """Query the knowledge base for similar past decisions."""
    memory_system = get_memory_system()
    return memory_system.query_knowledge(query, **kwargs)

def get_conversation_context(max_messages: int = 20, as_string: bool = False):
    """Get recent conversation context.

    Args:
        max_messages: Maximum number of messages to return
        as_string: If True, return formatted string; if False, return list of dicts

    Returns:
        List of message dicts or formatted string
    """
    memory_system = get_memory_system()
    return memory_system.get_conversation_context(max_messages, as_string)

if __name__ == "__main__":
    # Test the memory system
    print("Testing Persistent Memory System...")
    memory = get_memory_system()

    # Test adding knowledge
    test_metadata = {
        'genre': 'techno',
        'energy_level': 'high',
        'bpm_range': '128-132',
        'reasoning': 'Perfect peak-time energy for techno'
    }
    add_knowledge('track_selection', 'Selected high-energy techno track with 130 BPM for peak set',
                  test_metadata, 0.9)

    # Test querying knowledge
    results = query_knowledge_base('techno track selection')
    print(f"Found {len(results)} similar decisions:")
    for result in results:
        print(f"  - {result.metadata.get('decision_type', 'unknown')}: {result.page_content[:100]}...")

    # Test conversation memory
    memory.conversation_history.append(HumanMessage(content="I want to play techno music"))
    memory.conversation_history.append(AIMessage(content="I recommend selecting high-energy techno tracks in the 128-132 BPM range for optimal peak-time energy"))

    context = get_conversation_context(as_string=True)
    print(f"\n[OK] Conversation context:\n{context}")

    # Display stats
    stats = memory.get_memory_stats()
    print(f"Memory stats: {stats}")