#!/usr/bin/env python3
"""
Test script for the performance tracking system.

This script tests the PerfTracker and WebSocketPerfIntegration classes.
"""

import asyncio
import logging
import sys
import time
from pathlib import Path

# Add the parent directory to the path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from utils.perf_tracker import PerfTracker, PerformanceMonitor
from websocket import CodaWebSocketServer
from websocket.perf_integration import WebSocketPerfIntegration

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("performance_tracking_test")

async def test_perf_tracker():
    """Test the PerfTracker class."""
    # Initialize the PerfTracker
    tracker = PerfTracker(
        enable_system_monitoring=True,
        monitoring_interval=1.0,
        event_callback=lambda event_type, data: logger.info(f"Event: {event_type}, Data: {data}")
    )
    
    try:
        # Get system info
        logger.info("Getting system information...")
        system_info = tracker.get_system_info()
        logger.info(f"System info: {system_info}")
        
        # Test marking components
        logger.info("Testing component marking...")
        
        # Mark the start of a component operation
        tracker.mark_component("test", "operation1", start=True)
        
        # Simulate some work
        logger.info("Simulating work...")
        time.sleep(0.5)
        
        # Mark the end of the component operation
        tracker.mark_component("test", "operation1", start=False)
        
        # Get component stats
        logger.info("Getting component statistics...")
        stats = tracker.get_component_stats()
        logger.info(f"Component stats: {stats}")
        
        # Test system metrics
        logger.info("Getting system metrics...")
        metrics = tracker.get_system_metrics()
        logger.info(f"System metrics: {metrics}")
        
        # Test latency trace
        logger.info("Testing latency trace...")
        
        # Mark some points
        tracker.mark("stt_start")
        time.sleep(0.2)
        tracker.mark("stt_end")
        
        tracker.mark("llm_start")
        time.sleep(0.3)
        tracker.mark("llm_end")
        
        tracker.mark("tts_start")
        time.sleep(0.1)
        tracker.mark("tts_end")
        
        # Get latency trace
        trace = tracker.get_latency_trace()
        logger.info(f"Latency trace: {trace}")
        
        # Wait for monitoring to run
        logger.info("Waiting for monitoring to run...")
        await asyncio.sleep(2)
        
        # Stop monitoring
        logger.info("Stopping monitoring...")
        tracker.stop_monitoring()
        
        # Reset the tracker
        logger.info("Resetting tracker...")
        tracker.reset()
        
        logger.info("PerfTracker test completed")
    except Exception as e:
        logger.error(f"Error in PerfTracker test: {e}", exc_info=True)
        tracker.stop_monitoring()

async def test_perf_integration(server):
    """Test the WebSocketPerfIntegration class."""
    # Initialize the WebSocketPerfIntegration
    integration = WebSocketPerfIntegration(
        server=server,
        monitoring_interval=1.0
    )
    
    try:
        # Send system info
        logger.info("Sending system information...")
        integration.send_system_info()
        
        # Test marking components
        logger.info("Testing component marking...")
        
        # Mark the start of a component operation
        integration.mark_component("test", "operation1", start=True)
        
        # Simulate some work
        logger.info("Simulating work...")
        time.sleep(0.5)
        
        # Mark the end of the component operation
        integration.mark_component("test", "operation1", start=False)
        
        # Send component stats
        logger.info("Sending component statistics...")
        integration.send_component_stats()
        
        # Test latency trace
        logger.info("Testing latency trace...")
        
        # Mark some points
        tracker = integration.get_tracker()
        tracker.mark("stt_start")
        time.sleep(0.2)
        tracker.mark("stt_end")
        
        tracker.mark("llm_start")
        time.sleep(0.3)
        tracker.mark("llm_end")
        
        tracker.mark("tts_start")
        time.sleep(0.1)
        tracker.mark("tts_end")
        
        # Send latency trace
        integration.send_latency_trace()
        
        # Wait for monitoring to run
        logger.info("Waiting for monitoring to run...")
        await asyncio.sleep(2)
        
        logger.info("WebSocketPerfIntegration test completed")
    except Exception as e:
        logger.error(f"Error in WebSocketPerfIntegration test: {e}", exc_info=True)

async def test_performance_monitor():
    """Test the PerformanceMonitor singleton."""
    # Get the singleton instance
    logger.info("Getting PerformanceMonitor instance...")
    monitor1 = PerformanceMonitor.get_instance(
        enable_system_monitoring=True,
        monitoring_interval=1.0
    )
    
    # Get another instance (should be the same)
    logger.info("Getting another PerformanceMonitor instance...")
    monitor2 = PerformanceMonitor.get_instance()
    
    # Check if they're the same
    logger.info(f"Instances are the same: {monitor1 is monitor2}")
    
    # Reset the instance
    logger.info("Resetting PerformanceMonitor instance...")
    PerformanceMonitor.reset_instance()
    
    # Get a new instance
    logger.info("Getting a new PerformanceMonitor instance...")
    monitor3 = PerformanceMonitor.get_instance()
    
    # Check if it's different
    logger.info(f"New instance is different: {monitor1 is not monitor3}")
    
    # Stop monitoring
    logger.info("Stopping monitoring...")
    monitor3.stop_monitoring()
    
    logger.info("PerformanceMonitor test completed")

async def main():
    """Main function."""
    # Create the WebSocket server
    server = CodaWebSocketServer()
    
    # Start the server
    await server.start()
    
    try:
        # Test the PerfTracker
        logger.info("Testing PerfTracker...")
        await test_perf_tracker()
        
        # Test the WebSocketPerfIntegration
        logger.info("Testing WebSocketPerfIntegration...")
        await test_perf_integration(server)
        
        # Test the PerformanceMonitor
        logger.info("Testing PerformanceMonitor...")
        await test_performance_monitor()
        
        # Keep the server running for a bit
        logger.info("Tests completed. Server will stop in 5 seconds.")
        await asyncio.sleep(5)
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")
    finally:
        # Stop the server
        await server.stop()
        logger.info("Server stopped")

if __name__ == "__main__":
    asyncio.run(main())
