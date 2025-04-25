#!/usr/bin/env python3
"""
Test script for the event loop manager.

This script tests the thread-safe event loop manager implementation.
"""

import asyncio
import logging
import sys
import time
import threading
import unittest
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

# Add the parent directory to the path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from websocket.event_loop_manager import (
    get_event_loop_manager,
    get_event_loop,
    run_coroutine_threadsafe
)

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("test_event_loop_manager")


class TestEventLoopManager(unittest.TestCase):
    """Test cases for the event loop manager."""

    def test_get_event_loop(self):
        """Test getting an event loop for the current thread."""
        # Get an event loop for the current thread
        loop = get_event_loop()

        # Check that it's a valid event loop
        self.assertIsInstance(loop, asyncio.AbstractEventLoop)

        # Create a new event loop and set it as the current loop
        # This ensures the loop is not closed
        new_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(new_loop)

        # Get the event loop again
        loop2 = get_event_loop()

        # Check that it's a valid event loop
        self.assertIsInstance(loop2, asyncio.AbstractEventLoop)

        # Check that it's not closed
        self.assertFalse(loop2.is_closed())

    def test_get_event_loop_manager(self):
        """Test getting the event loop manager."""
        # Get the event loop manager
        manager = get_event_loop_manager()

        # Check that it's a valid manager
        self.assertIsNotNone(manager)

        # Check that it has a get_event_loop method
        self.assertTrue(hasattr(manager, 'get_event_loop'))

        # Check that it has a run_coroutine_threadsafe method
        self.assertTrue(hasattr(manager, 'run_coroutine_threadsafe'))

    def test_multiple_threads(self):
        """Test getting event loops from multiple threads."""
        # Define a function to run in a thread
        def thread_func():
            # Get an event loop for this thread
            loop = get_event_loop()

            # Check that it's a valid event loop
            self.assertIsInstance(loop, asyncio.AbstractEventLoop)

            # Check that it's running or not closed
            self.assertTrue(not loop.is_closed())

            # Return the loop
            return loop

        # Create threads
        threads = []
        loops = []

        for i in range(5):
            thread = threading.Thread(target=lambda: loops.append(thread_func()))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Check that we got 5 loops
        self.assertEqual(len(loops), 5)

        # Check that all loops are different
        loop_ids = [id(loop) for loop in loops]
        self.assertEqual(len(set(loop_ids)), 5)

    def test_run_coroutine_threadsafe(self):
        """Test running a coroutine in a thread-safe way."""
        # Define a coroutine to run
        async def coro():
            await asyncio.sleep(0.1)
            return 42

        # Create a new event loop and set it as the current loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            # Run the coroutine in a thread-safe way
            future = asyncio.run_coroutine_threadsafe(coro(), loop)

            # Wait for the result
            result = future.result()

            # Check the result
            self.assertEqual(result, 42)
        finally:
            # Clean up
            loop.close()

    def test_cross_thread_coroutine(self):
        """Test running a coroutine from one thread in another thread's event loop."""
        # Create a new event loop for the main thread
        main_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(main_loop)

        # Start the loop in a separate thread to keep it running
        def run_loop():
            asyncio.set_event_loop(main_loop)
            main_loop.run_forever()

        loop_thread = threading.Thread(target=run_loop, daemon=True)
        loop_thread.start()

        try:
            # Define a coroutine to run
            async def coro():
                await asyncio.sleep(0.1)
                return threading.get_ident()

            # Define a function to run in a thread
            results = []

            def thread_func():
                # Run the coroutine in the main thread's event loop
                future = asyncio.run_coroutine_threadsafe(coro(), main_loop)

                try:
                    # Wait for the result
                    result = future.result(timeout=1.0)

                    # Store the result
                    results.append(result)
                except Exception as e:
                    print(f"Error in thread_func: {e}")

            # Create a thread
            thread = threading.Thread(target=thread_func)
            thread.start()

            # Wait for the thread to complete
            thread.join()

            # Check that we got a result
            self.assertEqual(len(results), 1)

            # Check that the result is the loop thread's ID
            self.assertEqual(results[0], loop_thread.ident)
        finally:
            # Stop the loop
            main_loop.call_soon_threadsafe(main_loop.stop)

            # Wait for the loop thread to complete
            loop_thread.join(timeout=1.0)

            # Close the loop
            main_loop.close()

    def test_close_all_loops(self):
        """Test closing all event loops."""
        # Get the event loop manager
        manager = get_event_loop_manager()

        # Create a new event loop for testing
        test_loop = asyncio.new_event_loop()

        # Create some threads with event loops
        def thread_func():
            # Sleep to keep the thread alive
            time.sleep(0.5)

        # Create threads
        threads = []

        for i in range(3):
            thread = threading.Thread(target=thread_func)
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Store the test loop in the manager
        manager._loops[threading.get_ident()] = test_loop

        # Close all loops
        manager.close_all_loops()

        # Check that the test loop is closed
        self.assertTrue(test_loop.is_closed())


if __name__ == "__main__":
    unittest.main()
