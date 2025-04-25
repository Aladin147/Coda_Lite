"""
Memory System Fixes

This module contains fixes for the memory system that can be imported and applied
to the main codebase. It patches the memory system components to improve persistence,
retrieval, and encoding.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

from .enhanced_memory_manager import EnhancedMemoryManager
from .long_term import LongTermMemory
from .encoder import MemoryEncoder

logger = logging.getLogger("coda.memory.fixes")

def apply_memory_fixes():
    """Apply all memory system fixes."""
    logger.info("Applying memory system fixes")
    
    # Apply fixes
    persistence_fixes = fix_memory_persistence()
    retrieval_fixes = fix_memory_retrieval()
    encoding_fixes = fix_memory_encoding()
    integration_fixes = fix_memory_integration()
    vector_db_fixes = fix_vector_database()
    
    logger.info("Memory system fixes applied successfully")
    
    return {
        "persistence_fixes": persistence_fixes,
        "retrieval_fixes": retrieval_fixes,
        "encoding_fixes": encoding_fixes,
        "integration_fixes": integration_fixes,
        "vector_db_fixes": vector_db_fixes
    }

def fix_memory_persistence():
    """Fix memory persistence issues."""
    logger.info("Fixing memory persistence issues")
    
    # Patch EnhancedMemoryManager.add_turn to force more frequent persistence
    original_add_turn = EnhancedMemoryManager.add_turn
    
    def patched_add_turn(self, role: str, content: str) -> Dict[str, Any]:
        """Patched add_turn method with more aggressive persistence."""
        # Call original method
        turn = original_add_turn(self, role, content)
        
        # Force persistence after assistant turns
        if role == "assistant" and self.auto_persist:
            # Check if we have enough turns since last persist
            turns_since_persist = self.short_term.turn_count - self.turn_count_at_last_persist
            if turns_since_persist >= 1:  # Persist after every assistant turn
                self.persist_short_term_memory()
        
        return turn
    
    # Apply the patch
    EnhancedMemoryManager.add_turn = patched_add_turn
    logger.info("Patched EnhancedMemoryManager.add_turn for more frequent persistence")
    
    # Patch EnhancedMemoryManager.close to ensure persistence
    original_close = EnhancedMemoryManager.close
    
    def patched_close(self) -> None:
        """Patched close method to ensure persistence."""
        # Force persistence regardless of auto_persist setting
        self.persist_short_term_memory()
        
        # Call original method
        original_close(self)
    
    # Apply the patch
    EnhancedMemoryManager.close = patched_close
    logger.info("Patched EnhancedMemoryManager.close to ensure persistence")
    
    return {
        "add_turn_patched": True,
        "close_patched": True
    }

def fix_memory_retrieval():
    """Fix memory retrieval issues."""
    logger.info("Fixing memory retrieval issues")
    
    # Patch EnhancedMemoryManager.retrieve_relevant_memories to use lower similarity threshold
    original_retrieve_memories = EnhancedMemoryManager.retrieve_relevant_memories
    
    def patched_retrieve_memories(self, query: str, limit: int = 3, min_similarity: float = 0.5) -> List[Dict[str, Any]]:
        """Patched retrieve_relevant_memories method with lower similarity threshold."""
        # Use a lower threshold for better recall
        adjusted_min_similarity = 0.3  # Lower threshold for better recall
        
        # Call original method with adjusted threshold
        return original_retrieve_memories(self, query, limit, adjusted_min_similarity)
    
    # Apply the patch
    EnhancedMemoryManager.retrieve_relevant_memories = patched_retrieve_memories
    logger.info("Patched EnhancedMemoryManager.retrieve_relevant_memories with lower similarity threshold")
    
    # Patch EnhancedMemoryManager.get_enhanced_context to include more memories
    original_get_enhanced_context = EnhancedMemoryManager.get_enhanced_context
    
    def patched_get_enhanced_context(self, user_input: str, max_tokens: int = 800, max_memories: int = 3, include_system: bool = True) -> List[Dict[str, str]]:
        """Patched get_enhanced_context method to include more memories."""
        # Increase max_memories for better recall
        adjusted_max_memories = 5  # Include more memories
        
        # Call original method with adjusted max_memories
        return original_get_enhanced_context(self, user_input, max_tokens, adjusted_max_memories, include_system)
    
    # Apply the patch
    EnhancedMemoryManager.get_enhanced_context = patched_get_enhanced_context
    logger.info("Patched EnhancedMemoryManager.get_enhanced_context to include more memories")
    
    return {
        "retrieve_memories_patched": True,
        "get_enhanced_context_patched": True
    }

def fix_memory_encoding():
    """Fix memory encoding issues."""
    logger.info("Fixing memory encoding issues")
    
    # Patch MemoryEncoder._extract_topics to improve topic extraction
    original_extract_topics = MemoryEncoder._extract_topics
    
    def patched_extract_topics(self, text: str) -> List[str]:
        """Patched _extract_topics method with improved topic extraction."""
        # Call original method
        topics = original_extract_topics(self, text)
        
        # Add additional topic extraction logic
        # Look for common personal information patterns
        lower_text = text.lower()
        
        # Check for name mentions
        if "name is" in lower_text or "my name" in lower_text:
            topics.append("name")
        
        # Check for preference mentions
        if "like" in lower_text or "love" in lower_text or "prefer" in lower_text or "favorite" in lower_text:
            topics.append("preferences")
        
        # Check for project mentions
        if "project" in lower_text or "working on" in lower_text or "developing" in lower_text:
            topics.append("projects")
        
        # Check for location mentions
        if "live in" in lower_text or "from" in lower_text or "location" in lower_text:
            topics.append("location")
        
        # Remove duplicates
        topics = list(set(topics))
        
        return topics
    
    # Apply the patch
    MemoryEncoder._extract_topics = patched_extract_topics
    logger.info("Patched MemoryEncoder._extract_topics with improved topic extraction")
    
    # Patch MemoryEncoder._calculate_importance to improve importance scoring
    original_calculate_importance = MemoryEncoder._calculate_importance
    
    def patched_calculate_importance(self, text: str) -> float:
        """Patched _calculate_importance method with improved importance scoring."""
        # Call original method
        importance = original_calculate_importance(self, text)
        
        # Add additional importance scoring logic
        lower_text = text.lower()
        
        # Increase importance for personal information
        if "name is" in lower_text or "my name" in lower_text:
            importance += 0.2
        
        # Increase importance for preferences
        if "like" in lower_text or "love" in lower_text or "prefer" in lower_text or "favorite" in lower_text:
            importance += 0.1
        
        # Increase importance for project information
        if "project" in lower_text or "working on" in lower_text or "developing" in lower_text:
            importance += 0.15
        
        # Cap importance at 1.0
        importance = min(importance, 1.0)
        
        return importance
    
    # Apply the patch
    MemoryEncoder._calculate_importance = patched_calculate_importance
    logger.info("Patched MemoryEncoder._calculate_importance with improved importance scoring")
    
    return {
        "extract_topics_patched": True,
        "calculate_importance_patched": True
    }

def fix_memory_integration():
    """Fix memory integration issues."""
    logger.info("Fixing memory integration issues")
    
    # Patch EnhancedMemoryManager.get_enhanced_context to improve memory formatting
    original_get_enhanced_context = EnhancedMemoryManager.get_enhanced_context
    
    def patched_get_enhanced_context(self, user_input: str, max_tokens: int = 800, max_memories: int = 3, include_system: bool = True) -> List[Dict[str, str]]:
        """Patched get_enhanced_context method with improved memory formatting."""
        # Get short-term context
        context = self.short_term.get_context(max_tokens=max_tokens)
        
        # Retrieve relevant memories
        memories = self.retrieve_relevant_memories(user_input, limit=max_memories)
        
        # Store the retrieved memories for later access
        self.last_retrieved_memories = memories
        
        # If we have memories, add them to the context
        if memories:
            # Find position to insert memories (after system message if present)
            insert_pos = 1 if context and context[0]["role"] == "system" else 0
            
            # Format memories in a more structured way
            memory_content = "Important information I know about you:\n\n"
            
            # Group memories by topic
            topic_memories = {}
            for memory in memories:
                content = memory.get("content", "")
                metadata = memory.get("metadata", {})
                topics = metadata.get("topics", "").split(",") if isinstance(metadata.get("topics"), str) else []
                
                # Default topic if none found
                if not topics or topics == [""]:
                    topics = ["general"]
                
                for topic in topics:
                    if topic not in topic_memories:
                        topic_memories[topic] = []
                    topic_memories[topic].append(content)
            
            # Add memories by topic
            for topic, topic_content in topic_memories.items():
                if topic and topic != "":
                    memory_content += f"About {topic}:\n"
                    for i, content in enumerate(topic_content):
                        memory_content += f"- {content}\n"
                    memory_content += "\n"
            
            # Insert memories
            context.insert(insert_pos, {
                "role": "system",
                "content": memory_content
            })
            
            logger.info(f"Added {len(memories)} memories to context, grouped by topic")
        
        return context
    
    # Apply the patch
    EnhancedMemoryManager.get_enhanced_context = patched_get_enhanced_context
    logger.info("Patched EnhancedMemoryManager.get_enhanced_context with improved memory formatting")
    
    return {
        "get_enhanced_context_patched": True
    }

def fix_vector_database():
    """Fix vector database issues."""
    logger.info("Fixing vector database issues")
    
    # Patch LongTermMemory._save_metadata to ensure proper persistence
    original_save_metadata = LongTermMemory._save_metadata
    
    def patched_save_metadata(self, metadata=None) -> None:
        """Patched _save_metadata method to ensure proper persistence."""
        # Use provided metadata or instance metadata
        metadata_to_save = metadata if metadata is not None else self.metadata
        
        # Update last_updated timestamp
        metadata_to_save["last_updated"] = datetime.now().isoformat()
        
        # Save metadata to file
        try:
            with open(self.metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata_to_save, f, indent=2, default=str)
            
            logger.debug(f"Saved metadata with {len(metadata_to_save.get('memories', []))} memories")
        except Exception as e:
            logger.error(f"Error saving metadata: {e}")
            
            # Try to save to a backup location
            backup_path = f"{self.metadata_path}.backup"
            try:
                with open(backup_path, 'w', encoding='utf-8') as f:
                    json.dump(metadata_to_save, f, indent=2, default=str)
                logger.info(f"Saved metadata to backup location: {backup_path}")
            except Exception as backup_error:
                logger.error(f"Error saving metadata to backup location: {backup_error}")
    
    # Apply the patch
    LongTermMemory._save_metadata = patched_save_metadata
    logger.info("Patched LongTermMemory._save_metadata to ensure proper persistence")
    
    # Patch LongTermMemory.add_memory to ensure proper persistence
    original_add_memory = LongTermMemory.add_memory
    
    def patched_add_memory(self, content: str, source_type: str = "conversation", importance: float = 0.5, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Patched add_memory method to ensure proper persistence."""
        # Call original method
        memory_id = original_add_memory(self, content, source_type, importance, metadata)
        
        # Force metadata save
        self._save_metadata()
        
        return memory_id
    
    # Apply the patch
    LongTermMemory.add_memory = patched_add_memory
    logger.info("Patched LongTermMemory.add_memory to ensure proper persistence")
    
    return {
        "save_metadata_patched": True,
        "add_memory_patched": True
    }
