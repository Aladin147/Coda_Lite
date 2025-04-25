# Memory Summarization System

The Memory Summarization System provides mechanisms for summarizing memories, clustering related memories by topic, and generating user profiles in Coda Lite.

## Memory Summarization Core

The Memory Summarization System implements topic clustering and summarization algorithms for different memory types, providing a comprehensive view of Coda's memory.

### Features

- **Topic Clustering**: Group related memories by topic
- **Memory Summarization**: Generate summaries of memory clusters
- **User Profile Generation**: Create user profiles from preferences and facts
- **Recent Memory Summarization**: Summarize recent memories from the past N days
- **Memory Type Summarization**: Summarize memories of specific types
- **WebSocket Integration**: Emit events for dashboard visualization

### Components

#### MemorySummarizationSystem

The core summarization system that manages memory clustering and summarization.

- **Cluster Memories by Topic**: Group related memories by topic
- **Summarize Topic Cluster**: Generate a summary for a topic cluster
- **Generate Topic Summaries**: Create summaries for all topic clusters
- **Generate User Profile**: Create a user profile from preferences and facts
- **Summarize Recent Memories**: Summarize memories from the past N days
- **Summarize Memory by Type**: Summarize memories of a specific type
- **Get Memory Overview**: Get a comprehensive overview of the memory system

#### WebSocketEnhancedSummarization

Extends the MemorySummarizationSystem with WebSocket event emission for dashboard integration.

- **Emit Clustering Events**: Emit events for memory clustering
- **Emit Summary Events**: Emit events for memory summarization
- **Emit Profile Events**: Emit events for user profile generation
- **Emit Overview Events**: Emit events for memory overview

## Integration with EnhancedMemoryManager

The Memory Summarization System is integrated into the EnhancedMemoryManager, providing a unified interface for memory management.

### Methods

- **cluster_memories_by_topic**: Group related memories by topic
- **generate_topic_summaries**: Create summaries for all topic clusters
- **generate_user_profile**: Create a user profile from preferences and facts
- **summarize_recent_memories**: Summarize memories from the past N days
- **summarize_memory_by_type**: Summarize memories of a specific type
- **get_memory_overview**: Get a comprehensive overview of the memory system

## WebSocket Events

The Memory Summarization System emits the following WebSocket events:

- **memory_topic_clusters**: Emitted when memories are clustered by topic
- **memory_topic_summary**: Emitted when a topic cluster is summarized
- **memory_topic_summaries**: Emitted when all topic clusters are summarized
- **memory_user_profile**: Emitted when a user profile is generated
- **memory_recent_summary**: Emitted when recent memories are summarized
- **memory_type_summary**: Emitted when memories of a specific type are summarized
- **memory_cache_cleared**: Emitted when the summary cache is cleared
- **memory_overview**: Emitted when a memory overview is generated

## Usage

### Clustering Memories by Topic

```python
# Cluster memories by topic
clusters = memory_manager.cluster_memories_by_topic()
```

### Generating Topic Summaries

```python
# Generate summaries for all topic clusters
summaries = memory_manager.generate_topic_summaries()
```

### Generating User Profile

```python
# Generate a user profile
profile = memory_manager.generate_user_profile()
```

### Summarizing Recent Memories

```python
# Summarize memories from the past 7 days
summary = memory_manager.summarize_recent_memories(days=7, limit=10)
```

### Summarizing Memory by Type

```python
# Summarize preference memories
summary = memory_manager.summarize_memory_by_type("preference", limit=10)
```

### Getting Memory Overview

```python
# Get a comprehensive overview of the memory system
overview = memory_manager.get_memory_overview()
```

## Configuration

The Memory Summarization System can be configured through the Coda Lite configuration system:

```yaml
memory:
  # Summarization settings
  min_cluster_size: 3  # Minimum size of a memory cluster
  max_summary_length: 200  # Maximum length of a summary
  summary_cache_ttl: 3600  # Cache TTL in seconds
  topic_similarity_threshold: 0.7  # Threshold for topic similarity
  max_topics_per_cluster: 5  # Maximum number of topics per cluster
  profile_update_interval: 86400  # Profile update interval in seconds
```

## Dashboard Integration

The Memory Summarization System integrates with the dashboard through WebSocket events, providing real-time visualization of memory summaries and clusters.

### Memory Clusters Visualization

The dashboard can visualize memory clusters as a graph or tree, showing the relationships between memories and topics.

### Memory Summaries Display

The dashboard can display memory summaries for each topic cluster, providing a high-level overview of the memory system.

### User Profile Display

The dashboard can display the user profile, showing preferences, facts, and topics of interest.

### Memory Overview Display

The dashboard can display a comprehensive overview of the memory system, including statistics, clusters, and summaries.
