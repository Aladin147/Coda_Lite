# Active Recall and Self-testing Framework

The Active Recall and Self-testing Framework provides mechanisms for memory reinforcement, review, and integrity verification in Coda Lite.

## Active Recall System

The Active Recall System implements spaced repetition and memory reinforcement through recall, helping Coda maintain important memories over time.

### Features

- **Spaced Repetition**: Schedule memory reviews based on importance and review history
- **Memory Reinforcement**: Strengthen memories through successful recall
- **Review Tracking**: Track review history and success rates
- **Memory Health Metrics**: Monitor memory health and review status
- **WebSocket Integration**: Emit events for dashboard visualization

### Components

#### ActiveRecallSystem

The core active recall system that manages memory reviews and reinforcement.

- **Schedule Reviews**: Schedule memories for review based on importance
- **Get Due Reviews**: Retrieve memories due for review
- **Record Reviews**: Record review results and adjust review intervals
- **Generate Review Questions**: Create questions for memory review
- **Verify Memory Integrity**: Check for memory inconsistencies
- **Run Scheduled Tasks**: Perform periodic maintenance tasks
- **Get Memory Health Metrics**: Retrieve metrics about memory health

#### WebSocketEnhancedActiveRecall

Extends the ActiveRecallSystem with WebSocket event emission for dashboard integration.

- **Emit Review Events**: Emit events for review scheduling, completion, and results
- **Emit Maintenance Events**: Emit events for maintenance tasks
- **Emit Metrics Events**: Emit events for memory health metrics

## Self-testing Framework

The Self-testing Framework provides mechanisms for verifying memory integrity and testing retrieval accuracy.

### Features

- **Consistency Checks**: Verify memory consistency across storage systems
- **Inconsistency Repair**: Detect and repair corrupted memories
- **Retrieval Testing**: Test memory retrieval accuracy
- **Test Memory Generation**: Generate test memories for verification
- **WebSocket Integration**: Emit events for dashboard visualization

### Components

#### MemorySelfTestingFramework

The core self-testing framework that manages memory verification and testing.

- **Run Consistency Checks**: Verify memory consistency
- **Repair Inconsistencies**: Fix detected inconsistencies
- **Test Memory Retrieval**: Test retrieval accuracy
- **Generate Test Memories**: Create test memories for verification
- **Run Retrieval Test Suite**: Run a suite of retrieval tests
- **Get Metrics**: Retrieve metrics about self-testing

#### WebSocketEnhancedSelfTesting

Extends the MemorySelfTestingFramework with WebSocket event emission for dashboard integration.

- **Emit Consistency Check Events**: Emit events for consistency checks
- **Emit Repair Events**: Emit events for inconsistency repairs
- **Emit Test Events**: Emit events for retrieval tests
- **Emit Metrics Events**: Emit events for self-testing metrics

## Integration with EnhancedMemoryManager

The Active Recall and Self-testing Framework is integrated into the EnhancedMemoryManager, providing a unified interface for memory management.

### Methods

- **get_due_reviews**: Get memories due for review
- **generate_review_question**: Generate a review question for a memory
- **record_review**: Record a memory review result
- **reinforce_memory**: Reinforce a memory to make it more resistant to forgetting
- **run_memory_maintenance**: Run memory maintenance tasks
- **test_memory_retrieval**: Test memory retrieval accuracy
- **run_retrieval_test_suite**: Run a suite of retrieval tests

## WebSocket Events

The Active Recall and Self-testing Framework emits the following WebSocket events:

### Active Recall Events

- **memory_review_scheduled**: Emitted when a memory is scheduled for review
- **memory_reviews_due**: Emitted when memories are due for review
- **memory_review_recorded**: Emitted when a memory review is recorded
- **memory_review_question**: Emitted when a review question is generated
- **memory_maintenance_completed**: Emitted when maintenance tasks are completed
- **memory_health_metrics**: Emitted when memory health metrics are retrieved

### Self-testing Events

- **memory_consistency_check**: Emitted when a consistency check is run
- **memory_repairs**: Emitted when inconsistencies are repaired
- **memory_retrieval_test**: Emitted when a retrieval test is run
- **memory_test_suite**: Emitted when a retrieval test suite is run
- **memory_self_testing_metrics**: Emitted when self-testing metrics are retrieved

## Usage

### Scheduling Reviews

```python
# Schedule a memory for review
memory_manager.active_recall.schedule_review(memory_id, importance)
```

### Getting Due Reviews

```python
# Get memories due for review
due_reviews = memory_manager.get_due_reviews(limit=5)
```

### Generating Review Questions

```python
# Generate a review question for a memory
question = memory_manager.generate_review_question(memory)
```

### Recording Reviews

```python
# Record a memory review result
memory_manager.record_review(memory_id, success=True)
```

### Running Maintenance Tasks

```python
# Run memory maintenance tasks
results = memory_manager.run_memory_maintenance()
```

### Testing Retrieval

```python
# Test memory retrieval accuracy
results = memory_manager.test_memory_retrieval(query, expected_memory_ids)
```

### Running Test Suite

```python
# Run a suite of retrieval tests
results = memory_manager.run_retrieval_test_suite()
```

## Configuration

The Active Recall and Self-testing Framework can be configured through the Coda Lite configuration system:

```yaml
memory:
  # Active Recall settings
  min_review_interval: 1  # Minimum review interval in days
  max_review_interval: 60  # Maximum review interval in days
  initial_interval: 1  # Initial review interval in days
  interval_multiplier: 2.0  # Interval multiplier for successful reviews
  high_importance_threshold: 0.8  # Threshold for high importance memories
  medium_importance_threshold: 0.5  # Threshold for medium importance memories
  low_importance_threshold: 0.3  # Threshold for low importance memories
  verification_batch_size: 10  # Number of memories to verify in each batch
  verification_interval: 24  # Verification interval in hours
  
  # Self-testing settings
  self_test_interval: 24  # Self-test interval in hours
  self_test_batch_size: 10  # Number of memories to test in each batch
  repair_threshold: 0.7  # Threshold for automatic repair
```
