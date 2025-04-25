# Memory System Tests

This directory contains comprehensive tests for Coda's memory system. The tests cover all aspects of the memory system, including short-term memory, long-term memory, memory encoding, and WebSocket integration.

## Test Structure

The tests are organized into the following modules:

- `test_base.py`: Base test class with common setup/teardown logic
- `test_short_term_memory.py`: Tests for the short-term memory system
- `test_long_term_memory.py`: Tests for the long-term memory system
- `test_enhanced_memory_manager.py`: Tests for the enhanced memory manager
- `test_websocket_memory.py`: Tests for the WebSocket-enhanced memory manager
- `test_utils/memory_test_utils.py`: Utility classes and functions for testing
- `run_memory_tests.py`: Script to run all memory tests

## Test Coverage

The memory system tests cover the following components:

### 1. Short-Term Memory

- Conversation turn management
- Context generation with token limits
- Memory export and import
- Deque maxlen behavior for conversation history

### 2. Long-Term Memory

- Memory addition and retrieval
- Vector database integration (ChromaDB, SQLite, in-memory)
- Memory persistence across sessions
- Memory pruning when maximum capacity is reached
- Semantic search by content similarity
- Metadata-based search
- Topic extraction and management

### 3. Enhanced Memory Manager

- Integration of short-term and long-term memory
- Fact and preference storage
- Automatic memory persistence
- Enhanced context generation with relevant memories
- Topic extraction from user messages

### 4. WebSocket Memory Integration

- Event emission for memory operations
- Duplicate message detection
- Memory persistence with WebSocket events
- Memory retrieval with WebSocket events

## Running the Tests

To run all memory tests, use the following command from the project root:

```bash
python tests/memory/run_memory_tests.py
```

This will run all the tests and generate a comprehensive report in the `data/memory/test/results` directory.

## Test Results

Test results are saved in the following locations:

- Test logs: `data/memory/test/results/memory_tests_YYYYMMDD_HHMMSS.log`
- Test report: `data/memory/test/results/test_report_YYYYMMDD_HHMMSS.json`

The test report includes:

- Total number of tests run
- Number of tests passed, failed, and skipped
- Success rate
- Duration of the test run
- Details of any failures

## Recent Improvements

The memory system tests have been recently improved with the following enhancements:

1. **Robust Mock Implementations**: Enhanced mock implementations of memory system components to better simulate real-world behavior
2. **Improved Test Isolation**: Each test now runs in its own isolated environment with a unique test directory
3. **Better Error Handling**: Improved error handling and reporting for test failures
4. **WebSocket Integration Tests**: Added comprehensive tests for WebSocket integration with the memory system
5. **System Message Preservation**: Fixed tests for system message preservation in the conversation history
6. **Memory Pruning Tests**: Enhanced tests for memory pruning to ensure the most important memories are preserved
7. **Search Functionality Tests**: Improved tests for memory search functionality with better mock implementations

## Adding New Tests

To add new tests:

1. Create a new test class that inherits from `MemoryTestBase`
2. Add test methods to the class
3. Add the test class to the test suite in `run_memory_tests.py`

Example:

```python
class MyNewMemoryTest(MemoryTestBase):
    def test_new_feature(self):
        """Test a new memory feature."""
        # Test implementation here
        self.assertTrue(True)  # Assert expected behavior
```

Then add to `run_memory_tests.py`:

```python
def run_tests():
    # Create test suite
    suite = unittest.TestSuite()

    # Add existing test classes
    suite.addTest(unittest.makeSuite(ShortTermMemoryTest))
    suite.addTest(unittest.makeSuite(LongTermMemoryTest))
    suite.addTest(unittest.makeSuite(EnhancedMemoryManagerTest))
    suite.addTest(unittest.makeSuite(WebSocketMemoryTest))

    # Add new test class
    suite.addTest(unittest.makeSuite(MyNewMemoryTest))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result
```

## Test Data

Test data is stored in the following directories:

- `data/memory/test/long_term`: Long-term memory data for tests
- `data/memory/test/backups`: Backups of memory data
- `data/memory/test/results`: Test results and reports

Each test creates its own subdirectory with a unique timestamp to ensure test isolation.

## Dependencies

The tests require the following dependencies:

- ChromaDB (for vector database tests)
- sentence-transformers (for embedding tests)
- unittest (standard library)
- logging (standard library)
- json (standard library)

Make sure these dependencies are installed before running the tests.

## Troubleshooting

If you encounter issues with the tests:

1. Check the test logs for detailed error messages
2. Ensure all dependencies are installed
3. Check that the test directories exist and are writable
4. Try running individual test modules instead of the full suite
5. Use the `--verbose` flag for more detailed output:

   ```bash
   python tests/memory/run_memory_tests.py --verbose
   ```

## Continuous Integration

These tests are designed to be run as part of a continuous integration pipeline to ensure the memory system remains stable and functional as the codebase evolves.

## Documentation

For more detailed information about the memory system and its testing, see the following documentation:

- [Memory System Architecture](../../docs/MEMORY_SYSTEM_ARCHITECTURE.md)
- [WebSocket Memory Integration](../../docs/WEBSOCKET_MEMORY_INTEGRATION.md)
- [Memory System Fixes](../../docs/MEMORY_SYSTEM_FIXES.md)
