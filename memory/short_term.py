"""
Short-term memory management for Coda Lite.

This module provides a MemoryManager class for handling short-term conversation memory.
"""

import os
import json
import logging
from datetime import datetime
from collections import deque
from typing import List, Dict, Any, Optional, Union

logger = logging.getLogger("coda.memory")

class MemoryManager:
    """
    Manages short-term conversation memory for Coda.
    
    Responsibilities:
    - Store conversation turns (user/assistant messages)
    - Provide context for LLM within token limits
    - Support basic export/import for debugging
    
    Future extensibility:
    - Will serve as foundation for long-term memory
    - Designed to be extended with summarization and retrieval mechanisms
    """
    
    def __init__(self, max_turns: int = 20):
        """
        Initialize the memory manager.
        
        Args:
            max_turns: Maximum number of conversation turns to store
        """
        self.turns = deque(maxlen=max_turns)
        self.session_start = datetime.now().isoformat()
        self.turn_count = 0
        logger.info(f"MemoryManager initialized with max_turns={max_turns}")
    
    def add_turn(self, role: str, content: str) -> Dict[str, Any]:
        """
        Add a new conversation turn.
        
        Args:
            role: The speaker role ("system", "user", or "assistant")
            content: The message content
            
        Returns:
            The created turn object
        """
        if role not in ["system", "user", "assistant"]:
            logger.warning(f"Unknown role '{role}', expected 'system', 'user', or 'assistant'")
        
        turn = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "turn_id": self.turn_count
        }
        
        self.turns.append(turn)
        self.turn_count += 1
        
        logger.debug(f"Added turn {self.turn_count} with role '{role}'")
        return turn
    
    def get_context(self, max_tokens: int = 800) -> List[Dict[str, str]]:
        """
        Get conversation context within token budget.
        
        Args:
            max_tokens: Maximum number of tokens to include
            
        Returns:
            List of {"role": "...", "content": "..."} dicts for LLM context
        """
        context = []
        token_count = 0
        
        # Always include system message if present
        system_messages = [t for t in self.turns if t["role"] == "system"]
        if system_messages:
            system_message = system_messages[0]  # Use the first system message
            system_tokens = self._estimate_tokens(system_message["content"])
            context.append({
                "role": "system",
                "content": system_message["content"]
            })
            token_count += system_tokens
            logger.debug(f"Added system message to context ({system_tokens} tokens)")
        
        # Process non-system turns from newest to oldest
        non_system_turns = [t for t in self.turns if t["role"] != "system"]
        
        for turn in reversed(non_system_turns):
            # Estimate tokens
            turn_tokens = self._estimate_tokens(turn["content"])
            
            if token_count + turn_tokens <= max_tokens:
                # Add to beginning to maintain chronological order
                # (after system message if present)
                insert_pos = 1 if context and context[0]["role"] == "system" else 0
                context.insert(insert_pos, {
                    "role": turn["role"],
                    "content": turn["content"]
                })
                token_count += turn_tokens
                logger.debug(f"Added turn {turn['turn_id']} to context ({turn_tokens} tokens)")
            else:
                logger.debug(f"Skipped turn {turn['turn_id']} due to token limit")
                break
        
        logger.info(f"Generated context with {len(context)} turns and ~{token_count} tokens")
        return context
    
    def _estimate_tokens(self, text: str) -> int:
        """
        Estimate token count for a text string.
        
        Args:
            text: The text to estimate tokens for
            
        Returns:
            Estimated token count
            
        Note:
            This is a simple approximation. For more accurate counting,
            a proper tokenizer should be used.
        """
        # Simple approximation: ~4 chars per token for English text
        return max(1, len(text) // 4)
    
    def reset(self) -> bool:
        """
        Clear all conversation turns.
        
        Returns:
            True if successful
        """
        # Keep track of how many turns we're clearing
        turn_count = len(self.turns)
        
        # Clear the turns
        self.turns.clear()
        self.turn_count = 0
        
        logger.info(f"Memory reset, cleared {turn_count} turns")
        return True
    
    def export(self, path: Optional[str] = None) -> Union[str, Dict[str, Any]]:
        """
        Export memory to file or return as dict.
        
        Args:
            path: Optional file path to save the export
            
        Returns:
            File path if saved to file, or export data dict
        """
        export_data = {
            "session_start": self.session_start,
            "turn_count": self.turn_count,
            "export_time": datetime.now().isoformat(),
            "turns": list(self.turns)
        }
        
        if path:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(path), exist_ok=True)
            
            # Save to file
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Exported memory with {len(self.turns)} turns to {path}")
            return path
        else:
            logger.info(f"Generated memory export with {len(self.turns)} turns")
            return export_data
    
    def import_data(self, data_or_path: Union[str, Dict[str, Any]]) -> int:
        """
        Import memory from dict or file.
        
        Args:
            data_or_path: File path or data dict to import
            
        Returns:
            Number of turns imported
        """
        data = None
        
        if isinstance(data_or_path, str):
            # It's a path
            with open(data_or_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logger.info(f"Loaded memory data from {data_or_path}")
        else:
            # It's already a data dict
            data = data_or_path
            logger.info("Using provided memory data dict")
            
        # Reset current state
        self.reset()
        
        # Import metadata
        self.session_start = data.get("session_start", datetime.now().isoformat())
        self.turn_count = data.get("turn_count", 0)
        
        # Import turns
        for turn in data.get("turns", []):
            if "role" in turn and "content" in turn:
                self.turns.append(turn)
        
        logger.info(f"Imported {len(self.turns)} turns")
        return len(self.turns)
    
    def get_turn_count(self) -> int:
        """
        Get the number of turns in memory.
        
        Returns:
            Number of turns
        """
        return len(self.turns)
    
    def get_session_duration(self) -> float:
        """
        Get the duration of the current session in seconds.
        
        Returns:
            Session duration in seconds
        """
        start_time = datetime.fromisoformat(self.session_start)
        now = datetime.now()
        return (now - start_time).total_seconds()
