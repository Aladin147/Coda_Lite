"""
WebSocket integration for the memory self-testing framework.

This module provides a WebSocketEnhancedSelfTesting class that extends the MemorySelfTestingFramework
with WebSocket event emission.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from .self_testing import MemorySelfTestingFramework

logger = logging.getLogger("coda.memory.websocket_self_testing")

class WebSocketEnhancedSelfTesting(MemorySelfTestingFramework):
    """
    MemorySelfTestingFramework with WebSocket event emission.
    
    This class extends the MemorySelfTestingFramework to emit WebSocket events
    for self-testing operations.
    """
    
    def __init__(self, memory_manager, config: Dict[str, Any] = None, websocket_server=None):
        """
        Initialize the WebSocket-enhanced self-testing framework.
        
        Args:
            memory_manager: The memory manager to use
            config: Configuration dictionary
            websocket_server: WebSocket server for event emission
        """
        super().__init__(memory_manager, config)
        self.ws = websocket_server
        logger.info("WebSocketEnhancedSelfTesting initialized")
    
    def run_consistency_check(self, memory_ids: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Run a consistency check on memories and emit WebSocket event.
        
        Args:
            memory_ids: Optional list of memory IDs to check (if None, selects random sample)
            
        Returns:
            Dictionary with check results
        """
        # Call parent method
        results = super().run_consistency_check(memory_ids)
        
        # Emit WebSocket event
        if self.ws:
            self.ws.emit_event("memory_consistency_check", {
                "status": results.get("status"),
                "memories_checked": results.get("memories_checked", 0),
                "inconsistencies_found": len(results.get("inconsistencies", [])),
                "repairs_attempted": len(results.get("repairs", [])),
                "repairs_successful": sum(1 for repair in results.get("repairs", []) if repair.get("success", False)),
                "timestamp": datetime.now().isoformat()
            })
        
        return results
    
    def _repair_inconsistencies(self, inconsistencies: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Attempt to repair inconsistencies and emit WebSocket event.
        
        Args:
            inconsistencies: List of inconsistency dictionaries
            
        Returns:
            List of repair results
        """
        # Call parent method
        repairs = super()._repair_inconsistencies(inconsistencies)
        
        # Emit WebSocket event
        if self.ws and repairs:
            self.ws.emit_event("memory_repairs", {
                "repairs_attempted": len(repairs),
                "repairs_successful": sum(1 for repair in repairs if repair.get("success", False)),
                "repair_types": {
                    repair_type: sum(1 for repair in repairs if repair.get("type") == repair_type)
                    for repair_type in set(repair.get("type") for repair in repairs)
                },
                "timestamp": datetime.now().isoformat()
            })
        
        return repairs
    
    def test_memory_retrieval(self, query: str, expected_memory_ids: List[str]) -> Dict[str, Any]:
        """
        Test memory retrieval accuracy and emit WebSocket event.
        
        Args:
            query: Query to test
            expected_memory_ids: List of memory IDs that should be retrieved
            
        Returns:
            Dictionary with test results
        """
        # Call parent method
        results = super().test_memory_retrieval(query, expected_memory_ids)
        
        # Emit WebSocket event
        if self.ws:
            self.ws.emit_event("memory_retrieval_test", {
                "query": query,
                "expected_count": results.get("expected_count", 0),
                "retrieved_count": results.get("retrieved_count", 0),
                "precision": results.get("precision", 0),
                "recall": results.get("recall", 0),
                "f1_score": results.get("f1_score", 0),
                "timestamp": datetime.now().isoformat()
            })
        
        return results
    
    def run_retrieval_test_suite(self) -> Dict[str, Any]:
        """
        Run a suite of retrieval tests and emit WebSocket event.
        
        Returns:
            Dictionary with test results
        """
        # Call parent method
        results = super().run_retrieval_test_suite()
        
        # Emit WebSocket event
        if self.ws:
            self.ws.emit_event("memory_test_suite", {
                "tests_run": results.get("tests_run", 0),
                "average_precision": results.get("average_precision", 0),
                "average_recall": results.get("average_recall", 0),
                "average_f1": results.get("average_f1", 0),
                "timestamp": datetime.now().isoformat()
            })
        
        return results
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get metrics about self-testing and emit WebSocket event.
        
        Returns:
            Dictionary with self-testing metrics
        """
        # Call parent method
        metrics = super().get_metrics()
        
        # Emit WebSocket event
        if self.ws:
            self.ws.emit_event("memory_self_testing_metrics", {
                "metrics": metrics,
                "timestamp": datetime.now().isoformat()
            })
        
        return metrics
