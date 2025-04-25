# Temporal Weighting System

The Temporal Weighting System provides functionality to apply time-based decay to memory importance, implement recency bias in memory retrieval, and configure decay rates for different types of memories. This feature enhances Coda's memory system by making it more human-like, with memories naturally fading over time unless they are reinforced.

## Features

- **Time-based Decay**: Memories become less important over time based on configurable half-life values
- **Recency Bias**: More recent memories are prioritized in retrieval
- **Memory Type-specific Decay**: Different types of memories (facts, preferences, conversations) decay at different rates
- **Memory Reinforcement**: Memories can be reinforced to make them more resistant to forgetting
- **Forgetting Mechanism**: Less important and older memories can be automatically forgotten when memory pressure is high

## Configuration

The Temporal Weighting System can be configured in the `config.yaml` file:

```yaml
memory:
  # Other memory settings...
  
  # Temporal weighting settings
  default_decay_rate: 30.0  # Half-life in days for default memory decay
  # Decay rates for different memory types (half-life in days)
  conversation_decay_rate: 15.0  # Conversations decay faster
  fact_decay_rate: 60.0  # Facts decay slower
  preference_decay_rate: 90.0  # Preferences decay very slowly
  feedback_decay_rate: 45.0  # Feedback decays moderately
  summary_decay_rate: 30.0  # Summaries decay at default rate
  # Recency bias factor (higher = more bias towards recent memories)
  recency_bias: 1.0
  # Importance retention factor (higher = importance decays slower)
  importance_retention: 0.8
  # Reinforcement settings
  reinforcement_boost: 0.2  # How much reinforcement boosts importance
  max_reinforcement_count: 5  # Maximum number of reinforcements
```

## Usage

### Retrieving Memories with Temporal Weighting

```python
from memory import EnhancedMemoryManager

# Initialize memory manager
memory = EnhancedMemoryManager(config)

# Retrieve memories with temporal weighting
memories = memory.retrieve_relevant_memories(
    query="What are the user's favorite foods?",
    apply_temporal_weighting=True
)
```

### Reinforcing Memories

```python
# Reinforce a memory to make it more resistant to forgetting
memory.reinforce_memory(
    memory_id="memory_123",
    reinforcement_strength=1.0  # Full reinforcement
)
```

### Applying Forgetting Mechanism

```python
# Apply forgetting mechanism to remove less important memories
forgotten_count = memory.forget_memories()
```

## Implementation Details

The Temporal Weighting System is implemented in the following files:

- `memory/temporal_weighting.py`: Contains the `TemporalWeightingSystem` class that manages temporal weighting
- `memory/enhanced_memory_manager.py`: Contains the `EnhancedMemoryManager` class that integrates with the temporal weighting system
- `memory/long_term.py`: Contains the `LongTermMemory` class that stores memories with temporal metadata

## How It Works

### Decay Factor Calculation

The decay factor for a memory is calculated using an exponential decay formula:

```
decay_factor = 2^(-age/half_life)
```

Where:
- `age` is the age of the memory in days
- `half_life` is the decay rate for the memory type (in days)

This means that after `half_life` days, the memory's importance is reduced by 50%.

### Memory Scoring

When retrieving memories, the final score for each memory is calculated as:

```
final_score = (similarity * 0.4 + importance_weight * 0.3 + recency_score * 0.3) * decay_factor
```

Where:
- `similarity` is the semantic similarity to the query (0.0 to 1.0)
- `importance_weight` is the adjusted importance score (0.0 to 1.0)
- `recency_score` is the recency bias score (0.0 to 1.0)
- `decay_factor` is the time-based decay factor (0.0 to 1.0)

### Memory Reinforcement

When a memory is reinforced, the following changes occur:

1. The memory's timestamp is partially updated toward the current time
2. The memory's importance is increased
3. The memory's reinforcement count is incremented

### Forgetting Mechanism

The forgetting mechanism determines which memories to forget based on:

1. The memory's age
2. The memory's importance
3. The memory's type
4. The current memory pressure (how close the system is to the maximum memory limit)

## Future Enhancements

- **Emotional Weighting**: Add emotional significance as a factor in memory importance
- **Context-based Reinforcement**: Automatically reinforce memories that are frequently retrieved
- **Memory Consolidation**: Combine similar memories to reduce redundancy
- **Adaptive Decay Rates**: Adjust decay rates based on user interaction patterns
- **Memory Archiving**: Archive forgotten memories instead of deleting them completely
