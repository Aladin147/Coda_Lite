"""
WebSocket integration for performance tracking.

This module provides integration between the performance tracker and the WebSocket server.
"""

import logging
from typing import Dict, Any

from websocket.server import CodaWebSocketServer
from websocket.events import EventType
from utils.perf_tracker import PerformanceMonitor, PerfTracker

logger = logging.getLogger("coda.websocket.perf_integration")

class WebSocketPerfIntegration:
    """
    Integration between the performance tracker and the WebSocket server.
    
    This class provides methods to connect the performance tracker to the WebSocket server,
    allowing clients to receive real-time performance metrics.
    """
    
    def __init__(self, server: CodaWebSocketServer, monitoring_interval: float = 5.0):
        """
        Initialize the WebSocket performance integration.
        
        Args:
            server: The WebSocket server to use
            monitoring_interval: Interval in seconds for system monitoring
        """
        self.server = server
        
        # Initialize the performance tracker with a callback for events
        self.perf_tracker = PerformanceMonitor.get_instance(
            enable_system_monitoring=True,
            monitoring_interval=monitoring_interval,
            event_callback=self._handle_perf_event
        )
        
        logger.info(f"WebSocket performance integration initialized with monitoring interval {monitoring_interval}s")
        
    def _handle_perf_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """
        Handle performance events from the tracker.
        
        Args:
            event_type: The type of performance event
            data: The event data
        """
        if event_type == "system_metrics":
            # Send system metrics event
            self.server.push_event(
                EventType.SYSTEM_METRICS,
                {
                    "memory_mb": data.get("process_memory_mb", 0),
                    "cpu_percent": data.get("process_cpu_percent", 0),
                    "gpu_vram_mb": data.get("gpu_memory_used_mb", 0),
                    "uptime_seconds": data.get("uptime_seconds", 0)
                }
            )
            
            logger.debug("Sent system metrics event")
            
        elif event_type == "component_timing":
            # Send component timing event
            self.server.push_event(
                EventType.COMPONENT_TIMING,
                {
                    "component": data.get("component", "unknown"),
                    "operation": data.get("operation", "unknown"),
                    "duration_seconds": data.get("duration_seconds", 0)
                }
            )
            
            logger.debug(f"Sent component timing event: {data.get('component')}.{data.get('operation')}")
            
    def send_system_info(self) -> None:
        """Send system information to clients."""
        system_info = self.perf_tracker.get_system_info()
        
        # Send system info event
        self.server.push_event(
            EventType.SYSTEM_INFO,
            system_info,
            high_priority=True
        )
        
        logger.info("Sent system information")
        
    def send_latency_trace(self) -> None:
        """Send a latency trace to clients."""
        trace = self.perf_tracker.get_latency_trace()
        
        # Send latency trace event
        self.server.push_event(
            EventType.LATENCY_TRACE,
            trace
        )
        
        logger.debug(f"Sent latency trace: STT={trace.get('stt_seconds', 0):.2f}s, "
                    f"LLM={trace.get('llm_seconds', 0):.2f}s, "
                    f"TTS={trace.get('tts_seconds', 0):.2f}s, "
                    f"Total={trace.get('total_seconds', 0):.2f}s")
        
    def send_component_stats(self) -> None:
        """Send component statistics to clients."""
        stats = self.perf_tracker.get_component_stats()
        
        # Send component stats event
        self.server.push_event(
            EventType.COMPONENT_STATS,
            {
                "components": stats
            }
        )
        
        logger.debug(f"Sent component stats for {len(stats)} components")
        
    def mark_component(self, component: str, operation: str, start: bool = True) -> None:
        """
        Mark the start or end of a component operation.
        
        Args:
            component: The component name (e.g., "stt", "llm", "tts")
            operation: The operation name (e.g., "process", "initialize")
            start: Whether this is the start (True) or end (False) of the operation
        """
        self.perf_tracker.mark_component(component, operation, start)
        
    def get_tracker(self) -> PerfTracker:
        """
        Get the performance tracker instance.
        
        Returns:
            The performance tracker instance
        """
        return self.perf_tracker
