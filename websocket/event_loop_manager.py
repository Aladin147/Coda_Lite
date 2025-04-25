"""
Thread-safe event loop management for Coda's WebSocket implementation.

This module provides utilities for managing asyncio event loops across multiple threads.
"""

import asyncio
import threading
import logging
from typing import Dict, Optional

logger = logging.getLogger("coda.websocket.event_loop")

class EventLoopManager:
    """
    Thread-safe event loop manager.
    
    This class provides methods to get or create event loops for different threads,
    and to safely run coroutines across thread boundaries.
    """
    
    def __init__(self):
        """Initialize the event loop manager."""
        self._loops: Dict[int, asyncio.AbstractEventLoop] = {}
        self._lock = threading.RLock()
        self._main_loop: Optional[asyncio.AbstractEventLoop] = None
        
    def get_event_loop(self) -> asyncio.AbstractEventLoop:
        """
        Get the event loop for the current thread.
        
        If no event loop exists for the current thread, one will be created.
        
        Returns:
            The event loop for the current thread
        """
        thread_id = threading.get_ident()
        
        with self._lock:
            # Check if we already have a loop for this thread
            if thread_id in self._loops:
                return self._loops[thread_id]
            
            # Create a new event loop for this thread
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                # No event loop exists in this thread, create a new one
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
            # Store the loop
            self._loops[thread_id] = loop
            
            # If this is the main thread, store the main loop
            if threading.current_thread() is threading.main_thread():
                self._main_loop = loop
                logger.debug("Stored main thread event loop")
            
            logger.debug(f"Created new event loop for thread {thread_id}")
            return loop
    
    def get_main_loop(self) -> Optional[asyncio.AbstractEventLoop]:
        """
        Get the event loop for the main thread.
        
        Returns:
            The event loop for the main thread, or None if not set
        """
        with self._lock:
            return self._main_loop
    
    def set_main_loop(self, loop: asyncio.AbstractEventLoop) -> None:
        """
        Set the event loop for the main thread.
        
        Args:
            loop: The event loop to set
        """
        with self._lock:
            self._main_loop = loop
            self._loops[threading.get_ident()] = loop
            logger.debug("Set main thread event loop")
    
    def run_coroutine_threadsafe(self, coro, loop=None):
        """
        Run a coroutine in a thread-safe way.
        
        Args:
            coro: The coroutine to run
            loop: The event loop to run the coroutine in (default: main loop)
            
        Returns:
            A concurrent.futures.Future representing the result of the coroutine
        """
        if loop is None:
            loop = self.get_main_loop()
            if loop is None:
                loop = self.get_event_loop()
                
        return asyncio.run_coroutine_threadsafe(coro, loop)
    
    def close_all_loops(self) -> None:
        """Close all event loops."""
        with self._lock:
            for thread_id, loop in list(self._loops.items()):
                try:
                    loop.close()
                    logger.debug(f"Closed event loop for thread {thread_id}")
                except Exception as e:
                    logger.error(f"Error closing event loop for thread {thread_id}: {e}")
                    
            self._loops.clear()
            self._main_loop = None

# Global event loop manager instance
_event_loop_manager = EventLoopManager()

def get_event_loop_manager() -> EventLoopManager:
    """
    Get the global event loop manager instance.
    
    Returns:
        The global event loop manager instance
    """
    return _event_loop_manager

def get_event_loop() -> asyncio.AbstractEventLoop:
    """
    Get the event loop for the current thread.
    
    If no event loop exists for the current thread, one will be created.
    
    Returns:
        The event loop for the current thread
    """
    return _event_loop_manager.get_event_loop()

def run_coroutine_threadsafe(coro, loop=None):
    """
    Run a coroutine in a thread-safe way.
    
    Args:
        coro: The coroutine to run
        loop: The event loop to run the coroutine in (default: main loop)
        
    Returns:
        A concurrent.futures.Future representing the result of the coroutine
    """
    return _event_loop_manager.run_coroutine_threadsafe(coro, loop)
