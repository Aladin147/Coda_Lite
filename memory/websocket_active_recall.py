"""
WebSocket integration for the active recall system.

This module provides a WebSocketEnhancedActiveRecall class that extends the ActiveRecallSystem
with WebSocket event emission.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from .active_recall import ActiveRecallSystem

logger = logging.getLogger("coda.memory.websocket_active_recall")

class WebSocketEnhancedActiveRecall(ActiveRecallSystem):
    """
    ActiveRecallSystem with WebSocket event emission.
    
    This class extends the ActiveRecallSystem to emit WebSocket events
    for active recall operations.
    """
    
    def __init__(self, memory_manager, config: Dict[str, Any] = None, websocket_server=None):
        """
        Initialize the WebSocket-enhanced active recall system.
        
        Args:
            memory_manager: The memory manager to use
            config: Configuration dictionary
            websocket_server: WebSocket server for event emission
        """
        super().__init__(memory_manager, config)
        self.ws = websocket_server
        logger.info("WebSocketEnhancedActiveRecall initialized")
    
    def schedule_review(self, memory_id: str, importance: float, force_schedule: bool = False) -> datetime:
        """
        Schedule a memory for review and emit WebSocket event.
        
        Args:
            memory_id: The memory ID
            importance: The memory importance (0.0 to 1.0)
            force_schedule: Whether to force scheduling even if already scheduled
            
        Returns:
            Scheduled review time
        """
        # Call parent method
        next_review = super().schedule_review(memory_id, importance, force_schedule)
        
        # Emit WebSocket event
        if self.ws:
            memory = self.memory_manager.long_term.get_memory_by_id(memory_id)
            if memory:
                content_preview = memory.get("content", "")[:50] + "..." if len(memory.get("content", "")) > 50 else memory.get("content", "")
                
                self.ws.emit_event("memory_review_scheduled", {
                    "memory_id": memory_id,
                    "importance": importance,
                    "next_review": next_review.isoformat(),
                    "content_preview": content_preview,
                    "memory_type": memory.get("metadata", {}).get("source_type", "unknown"),
                    "timestamp": datetime.now().isoformat()
                })
        
        return next_review
    
    def get_due_reviews(self, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get memories due for review and emit WebSocket event.
        
        Args:
            limit: Maximum number of memories to return
            
        Returns:
            List of memories due for review
        """
        # Call parent method
        due_memories = super().get_due_reviews(limit)
        
        # Emit WebSocket event
        if self.ws and due_memories:
            self.ws.emit_event("memory_reviews_due", {
                "count": len(due_memories),
                "memories": [
                    {
                        "memory_id": memory.get("id"),
                        "content_preview": memory.get("content", "")[:50] + "..." if len(memory.get("content", "")) > 50 else memory.get("content", ""),
                        "memory_type": memory.get("metadata", {}).get("source_type", "unknown"),
                        "importance": memory.get("importance", 0.5)
                    }
                    for memory in due_memories
                ],
                "timestamp": datetime.now().isoformat()
            })
        
        return due_memories
    
    def record_review(self, memory_id: str, success: bool, interval: Optional[float] = None) -> None:
        """
        Record a memory review result and emit WebSocket event.
        
        Args:
            memory_id: The memory ID
            success: Whether the review was successful
            interval: Optional override for the review interval
        """
        # Call parent method
        super().record_review(memory_id, success, interval)
        
        # Emit WebSocket event
        if self.ws:
            memory = self.memory_manager.long_term.get_memory_by_id(memory_id)
            if memory:
                content_preview = memory.get("content", "")[:50] + "..." if len(memory.get("content", "")) > 50 else memory.get("content", "")
                
                self.ws.emit_event("memory_review_recorded", {
                    "memory_id": memory_id,
                    "success": success,
                    "content_preview": content_preview,
                    "memory_type": memory.get("metadata", {}).get("source_type", "unknown"),
                    "importance": memory.get("importance", 0.5),
                    "timestamp": datetime.now().isoformat()
                })
    
    def run_scheduled_tasks(self) -> Dict[str, Any]:
        """
        Run scheduled tasks for the active recall system and emit WebSocket event.
        
        Returns:
            Dictionary with task results
        """
        # Call parent method
        results = super().run_scheduled_tasks()
        
        # Emit WebSocket event
        if self.ws:
            self.ws.emit_event("memory_maintenance_completed", {
                "active_recall": {
                    "reviews_scheduled": results.get("reviews_scheduled", 0),
                    "verification": results.get("verification", {}).get("verified", False)
                },
                "timestamp": datetime.now().isoformat()
            })
        
        return results
    
    def get_memory_health_metrics(self) -> Dict[str, Any]:
        """
        Get metrics about memory health and review status and emit WebSocket event.
        
        Returns:
            Dictionary with memory health metrics
        """
        # Call parent method
        metrics = super().get_memory_health_metrics()
        
        # Emit WebSocket event
        if self.ws:
            self.ws.emit_event("memory_health_metrics", {
                "metrics": metrics,
                "timestamp": datetime.now().isoformat()
            })
        
        return metrics
