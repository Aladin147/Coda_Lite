# Coda Lite Debugging Tools

## Overview

This document outlines the debugging tools we're implementing to enhance the observability and troubleshooting capabilities of Coda Lite. These tools are designed to provide deep insights into the system's behavior, performance, and state, making it easier to identify and fix issues.

## Core Debugging Tools

### 1. ConversationPipelineDebugger

The ConversationPipelineDebugger is a comprehensive tool for tracking the flow of data through the conversation pipeline. It logs each stage's input, output, and performance metrics, providing a complete picture of the conversation flow.

#### Features:
- **Stage-by-Stage Logging**: Captures input and output for each pipeline stage
- **Performance Metrics**: Records timing information for each stage
- **Conversation Visualization**: Generates visual representations of conversation flow
- **Persistent Logging**: Saves debug logs for later analysis

#### Implementation:

```python
class ConversationPipelineDebugger:
    def __init__(self, enabled=True, log_level="INFO", output_dir=None):
        self.enabled = enabled
        self.logger = logging.getLogger("coda.pipeline.debugger")
        self.logger.setLevel(log_level)
        self.stages = []
        self.current_conversation_id = None
        self.output_dir = output_dir or Path.home() / ".coda" / "pipeline_logs"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def start_conversation(self, conversation_id=None):
        """Start tracking a new conversation."""
        self.current_conversation_id = conversation_id or str(uuid.uuid4())
        self.stages = []
        self.logger.info(f"Starting conversation: {self.current_conversation_id}")
        return self.current_conversation_id
        
    def log_stage(self, stage_name, input_data, output_data, metadata=None):
        """Log a pipeline stage with input, output, and timing information."""
        if not self.enabled:
            return
            
        timestamp = datetime.now()
        
        # Create stage record
        stage = {
            "conversation_id": self.current_conversation_id,
            "stage_name": stage_name,
            "timestamp": timestamp.isoformat(),
            "duration_ms": metadata.get("duration_ms") if metadata else None,
            "input": self._sanitize_data(input_data),
            "output": self._sanitize_data(output_data),
            "metadata": metadata or {}
        }
        
        # Add to stages list
        self.stages.append(stage)
        
        # Log summary
        self.logger.info(
            f"Stage: {stage_name} | "
            f"Duration: {stage['duration_ms']}ms | "
            f"Input size: {len(str(stage['input']))} chars | "
            f"Output size: {len(str(stage['output']))} chars"
        )
        
        return stage
        
    def end_conversation(self, save=True):
        """End the current conversation and optionally save the debug log."""
        if not self.enabled or not self.current_conversation_id:
            return
            
        # Calculate total duration
        if self.stages:
            first_stage = self.stages[0]
            last_stage = self.stages[-1]
            first_time = datetime.fromisoformat(first_stage["timestamp"])
            last_time = datetime.fromisoformat(last_stage["timestamp"])
            total_duration = (last_time - first_time).total_seconds() * 1000
            
            # Add duration to metadata
            for stage in self.stages:
                if stage.get("metadata") is None:
                    stage["metadata"] = {}
                stage["metadata"]["total_conversation_duration_ms"] = total_duration
        
        # Save to file if requested
        if save:
            self._save_conversation_log()
            
        # Log summary
        stage_names = [s["stage_name"] for s in self.stages]
        self.logger.info(
            f"Conversation {self.current_conversation_id} completed | "
            f"Stages: {' -> '.join(stage_names)} | "
            f"Total duration: {total_duration:.2f}ms"
        )
        
        return {
            "conversation_id": self.current_conversation_id,
            "stages": self.stages,
            "total_duration_ms": total_duration if self.stages else None
        }
        
    def _save_conversation_log(self):
        """Save the current conversation log to a file."""
        if not self.current_conversation_id or not self.stages:
            return
            
        # Create filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"pipeline_{self.current_conversation_id}_{timestamp}.json"
        filepath = self.output_dir / filename
        
        # Save as JSON
        with open(filepath, "w") as f:
            json.dump({
                "conversation_id": self.current_conversation_id,
                "stages": self.stages,
                "timestamp": datetime.now().isoformat()
            }, f, indent=2)
            
        self.logger.info(f"Saved pipeline debug log to {filepath}")
        
    def _sanitize_data(self, data):
        """Sanitize data for logging (remove sensitive info, truncate large content)."""
        # Implementation depends on data structure
        # This is a simple example
        if isinstance(data, str) and len(data) > 1000:
            return data[:1000] + "... [truncated]"
        return data
```

#### Integration:

The ConversationPipelineDebugger will be integrated into the ConversationManager:

```python
class ConversationManager:
    def __init__(self, config, debugger=None):
        self.config = config
        self.stt = STTModule(config.stt)
        self.llm = LLMModule(config.llm)
        self.tts = TTSModule(config.tts)
        self.memory = MemoryModule(config.memory)
        
        # Initialize debugger if not provided
        self.debugger = debugger or ConversationPipelineDebugger(
            enabled=config.debug.enabled,
            log_level=config.debug.log_level,
            output_dir=config.debug.output_dir
        )
        
    async def process_user_input(self, audio_data):
        # Start tracking conversation
        conversation_id = self.debugger.start_conversation()
        
        try:
            # STT Stage
            start_time = time.time()
            transcript = await self.stt.transcribe(audio_data)
            stt_duration = (time.time() - start_time) * 1000
            
            self.debugger.log_stage(
                "stt",
                {"audio_length": len(audio_data)},
                {"transcript": transcript},
                {"duration_ms": stt_duration}
            )
            
            # Memory Retrieval Stage
            start_time = time.time()
            context = await self.memory.get_context(transcript)
            memory_duration = (time.time() - start_time) * 1000
            
            self.debugger.log_stage(
                "memory_retrieval",
                {"query": transcript},
                {"context": context},
                {"duration_ms": memory_duration}
            )
            
            # LLM Stage
            start_time = time.time()
            response = await self.llm.generate(transcript, context)
            llm_duration = (time.time() - start_time) * 1000
            
            self.debugger.log_stage(
                "llm",
                {"query": transcript, "context": context},
                {"response": response},
                {"duration_ms": llm_duration}
            )
            
            # Memory Update Stage
            start_time = time.time()
            await self.memory.add_interaction(transcript, response)
            memory_update_duration = (time.time() - start_time) * 1000
            
            self.debugger.log_stage(
                "memory_update",
                {"user_message": transcript, "assistant_message": response},
                {"success": True},
                {"duration_ms": memory_update_duration}
            )
            
            # TTS Stage
            start_time = time.time()
            audio = await self.tts.synthesize(response)
            tts_duration = (time.time() - start_time) * 1000
            
            self.debugger.log_stage(
                "tts",
                {"text": response},
                {"audio_length": len(audio)},
                {"duration_ms": tts_duration}
            )
            
            # End conversation tracking
            self.debugger.end_conversation()
            
            return {
                "transcript": transcript,
                "response": response,
                "audio": audio,
                "conversation_id": conversation_id
            }
            
        except Exception as e:
            # Log error
            self.debugger.log_stage(
                "error",
                {"error": str(e)},
                {"traceback": traceback.format_exc()},
                {"error_type": type(e).__name__}
            )
            
            # End conversation tracking
            self.debugger.end_conversation()
            
            # Re-raise or handle error
            raise
```

### 2. Memory Snapshot Emitter

The Memory Snapshot Emitter captures the state of the memory system at regular intervals or after significant operations. This allows for visualization of memory evolution over time and helps identify issues with memory persistence or retrieval.

#### Features:
- **Regular Snapshots**: Captures memory state at configurable intervals
- **Operation-Triggered Snapshots**: Takes snapshots after significant operations
- **Comparison Tools**: Allows comparison between snapshots to identify changes
- **Visualization**: Provides tools for visualizing memory evolution

#### Implementation:

```python
class MemorySnapshotEmitter:
    def __init__(self, memory_manager, snapshot_dir=None, interval=10, enabled=True):
        self.memory_manager = memory_manager
        self.snapshot_dir = snapshot_dir or Path.home() / ".coda" / "memory_snapshots"
        self.snapshot_dir.mkdir(parents=True, exist_ok=True)
        self.interval = interval  # Take snapshot every N memory operations
        self.operation_count = 0
        self.enabled = enabled
        self.logger = logging.getLogger("coda.memory.snapshots")
        
    def after_memory_operation(self, operation_type, memory_id=None, query=None):
        """Called after any memory operation to potentially take a snapshot."""
        if not self.enabled:
            return
            
        self.operation_count += 1
        
        # Take snapshot at regular intervals
        if self.operation_count % self.interval == 0:
            self.take_snapshot(f"interval_{self.operation_count}")
            
        # Always take snapshot for certain operations
        if operation_type in ["clear", "import", "export"]:
            self.take_snapshot(f"{operation_type}_{datetime.now().strftime('%H%M%S')}")
            
    def take_snapshot(self, snapshot_id=None):
        """Take a snapshot of the current memory state."""
        snapshot_id = snapshot_id or f"snapshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Get memory data
        try:
            # Get short-term memory
            short_term = {
                "turns": list(self.memory_manager.short_term.turns),
                "turn_count": self.memory_manager.short_term.turn_count
            }
            
            # Get long-term memory
            long_term = {
                "memories": self.memory_manager.long_term.get_all_memories(),
                "memory_count": self.memory_manager.long_term.metadata.get("memory_count", 0),
                "topics": self.memory_manager.long_term.get_all_topics()
            }
            
            # Create snapshot
            snapshot = {
                "snapshot_id": snapshot_id,
                "timestamp": datetime.now().isoformat(),
                "operation_count": self.operation_count,
                "short_term": short_term,
                "long_term": long_term
            }
            
            # Save snapshot
            filename = f"memory_{snapshot_id}.json"
            filepath = self.snapshot_dir / filename
            
            with open(filepath, "w") as f:
                json.dump(snapshot, f, indent=2)
                
            self.logger.info(f"Memory snapshot saved to {filepath}")
            
            return filepath
            
        except Exception as e:
            self.logger.error(f"Failed to take memory snapshot: {e}")
            return None
            
    def compare_snapshots(self, snapshot_id1, snapshot_id2):
        """Compare two memory snapshots and return the differences."""
        # Load snapshots
        filepath1 = self.snapshot_dir / f"memory_{snapshot_id1}.json"
        filepath2 = self.snapshot_dir / f"memory_{snapshot_id2}.json"
        
        if not filepath1.exists() or not filepath2.exists():
            self.logger.error(f"Snapshot files not found")
            return None
            
        with open(filepath1, "r") as f1, open(filepath2, "r") as f2:
            snapshot1 = json.load(f1)
            snapshot2 = json.load(f2)
            
        # Compare memory counts
        diff = {
            "short_term": {
                "turn_count_diff": snapshot2["short_term"]["turn_count"] - snapshot1["short_term"]["turn_count"],
                "turns_added": len(snapshot2["short_term"]["turns"]) - len(snapshot1["short_term"]["turns"])
            },
            "long_term": {
                "memory_count_diff": snapshot2["long_term"]["memory_count"] - snapshot1["long_term"]["memory_count"],
                "topic_count_diff": len(snapshot2["long_term"]["topics"]) - len(snapshot1["long_term"]["topics"])
            },
            "new_memories": [],
            "removed_memories": []
        }
        
        # Find new and removed memories
        memories1_ids = {m["id"] for m in snapshot1["long_term"]["memories"]}
        memories2_ids = {m["id"] for m in snapshot2["long_term"]["memories"]}
        
        new_memory_ids = memories2_ids - memories1_ids
        removed_memory_ids = memories1_ids - memories2_ids
        
        # Get details of new memories
        diff["new_memories"] = [
            m for m in snapshot2["long_term"]["memories"] 
            if m["id"] in new_memory_ids
        ]
        
        # Get details of removed memories
        diff["removed_memories"] = [
            m for m in snapshot1["long_term"]["memories"] 
            if m["id"] in removed_memory_ids
        ]
        
        return diff
```

#### Integration:

The MemorySnapshotEmitter will be integrated into the EnhancedMemoryManager:

```python
class EnhancedMemoryManager:
    def __init__(self, config, snapshot_emitter=None):
        self.config = config
        self.short_term = ShortTermMemory(config.short_term)
        self.long_term = LongTermMemory(config.long_term)
        
        # Initialize snapshot emitter if not provided
        self.snapshot_emitter = snapshot_emitter or MemorySnapshotEmitter(
            memory_manager=self,
            snapshot_dir=config.debug.snapshot_dir,
            interval=config.debug.snapshot_interval,
            enabled=config.debug.snapshots_enabled
        )
        
    async def add_interaction(self, user_message, assistant_message):
        """Add a new interaction to memory."""
        # Add to short-term memory
        self.short_term.add_turn(user_message, assistant_message)
        
        # Extract and store important information in long-term memory
        memories = self._extract_memories(user_message, assistant_message)
        for memory in memories:
            await self.long_term.add_memory(memory)
            
        # Notify snapshot emitter
        self.snapshot_emitter.after_memory_operation("add_interaction")
        
        return True
        
    async def clear_memory(self):
        """Clear all memory."""
        self.short_term.clear()
        await self.long_term.clear()
        
        # Notify snapshot emitter
        self.snapshot_emitter.after_memory_operation("clear")
        
        return True
        
    async def export_memory(self, filepath):
        """Export memory to a file."""
        data = {
            "short_term": self.short_term.export(),
            "long_term": await self.long_term.export()
        }
        
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)
            
        # Notify snapshot emitter
        self.snapshot_emitter.after_memory_operation("export")
        
        return True
        
    async def import_memory(self, filepath):
        """Import memory from a file."""
        with open(filepath, "r") as f:
            data = json.load(f)
            
        self.short_term.import_data(data.get("short_term", {}))
        await self.long_term.import_data(data.get("long_term", {}))
        
        # Notify snapshot emitter
        self.snapshot_emitter.after_memory_operation("import")
        
        return True
```

### 3. Cache Debugger

The Cache Debugger provides visibility into the caching system, showing what's being reused versus recomputed. This helps identify opportunities for optimization and diagnose performance issues.

#### Features:
- **Cache Hit/Miss Tracking**: Records cache hits and misses
- **Cache Performance Metrics**: Measures time saved by cache hits
- **Cache Visualization**: Provides visual representation of cache usage
- **Cache Tuning Recommendations**: Suggests improvements to cache configuration

#### Implementation:

```python
class CacheDebugger:
    def __init__(self, enabled=True, log_level="INFO"):
        self.enabled = enabled
        self.logger = logging.getLogger("coda.cache.debugger")
        self.logger.setLevel(log_level)
        self.stats = {
            "hits": 0,
            "misses": 0,
            "time_saved_ms": 0,
            "cache_types": defaultdict(lambda: {"hits": 0, "misses": 0, "time_saved_ms": 0})
        }
        
    def record_cache_access(self, cache_type, key, hit, computation_time_ms=None):
        """Record a cache access (hit or miss)."""
        if not self.enabled:
            return
            
        # Update global stats
        if hit:
            self.stats["hits"] += 1
            if computation_time_ms:
                self.stats["time_saved_ms"] += computation_time_ms
        else:
            self.stats["misses"] += 1
            
        # Update cache-specific stats
        cache_stats = self.stats["cache_types"][cache_type]
        if hit:
            cache_stats["hits"] += 1
            if computation_time_ms:
                cache_stats["time_saved_ms"] += computation_time_ms
        else:
            cache_stats["misses"] += 1
            
        # Log access
        hit_status = "HIT" if hit else "MISS"
        self.logger.debug(
            f"Cache {hit_status}: {cache_type} | "
            f"Key: {key} | "
            f"Time saved: {computation_time_ms if hit else 0}ms"
        )
        
    def get_stats(self):
        """Get current cache statistics."""
        if not self.enabled:
            return {}
            
        # Calculate hit rates
        total = self.stats["hits"] + self.stats["misses"]
        hit_rate = self.stats["hits"] / total if total > 0 else 0
        
        cache_type_stats = {}
        for cache_type, stats in self.stats["cache_types"].items():
            type_total = stats["hits"] + stats["misses"]
            type_hit_rate = stats["hits"] / type_total if type_total > 0 else 0
            cache_type_stats[cache_type] = {
                **stats,
                "hit_rate": type_hit_rate,
                "total": type_total
            }
            
        return {
            "hits": self.stats["hits"],
            "misses": self.stats["misses"],
            "total": total,
            "hit_rate": hit_rate,
            "time_saved_ms": self.stats["time_saved_ms"],
            "cache_types": cache_type_stats
        }
        
    def get_recommendations(self):
        """Get recommendations for cache tuning."""
        if not self.enabled:
            return []
            
        recommendations = []
        stats = self.get_stats()
        
        # Check overall hit rate
        if stats["hit_rate"] < 0.5 and stats["total"] > 100:
            recommendations.append({
                "type": "general",
                "message": "Overall cache hit rate is low. Consider increasing cache size or TTL.",
                "hit_rate": stats["hit_rate"],
                "priority": "high" if stats["hit_rate"] < 0.3 else "medium"
            })
            
        # Check individual cache types
        for cache_type, type_stats in stats["cache_types"].items():
            # Low hit rate
            if type_stats["hit_rate"] < 0.4 and type_stats["total"] > 50:
                recommendations.append({
                    "type": "cache_type",
                    "cache_type": cache_type,
                    "message": f"Hit rate for {cache_type} cache is low. Consider tuning this cache.",
                    "hit_rate": type_stats["hit_rate"],
                    "priority": "high" if type_stats["hit_rate"] < 0.2 else "medium"
                })
                
            # High value cache with medium hit rate
            if type_stats["time_saved_ms"] > 5000 and 0.4 <= type_stats["hit_rate"] < 0.7:
                recommendations.append({
                    "type": "cache_type",
                    "cache_type": cache_type,
                    "message": f"{cache_type} cache is saving significant time but hit rate could be improved.",
                    "hit_rate": type_stats["hit_rate"],
                    "time_saved_ms": type_stats["time_saved_ms"],
                    "priority": "medium"
                })
                
        return recommendations
        
    def reset_stats(self):
        """Reset cache statistics."""
        self.stats = {
            "hits": 0,
            "misses": 0,
            "time_saved_ms": 0,
            "cache_types": defaultdict(lambda: {"hits": 0, "misses": 0, "time_saved_ms": 0})
        }
```

#### Integration:

The CacheDebugger will be integrated into our caching system:

```python
class CachedEmbedder:
    def __init__(self, model_name, cache_size=1000, cache_ttl=3600, debugger=None):
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)
        self.cache = LRUCache(maxsize=cache_size, ttl=cache_ttl)
        self.debugger = debugger or CacheDebugger(enabled=True)
        
    async def embed_text(self, text):
        """Embed text, using cache if available."""
        # Create cache key
        cache_key = f"{self.model_name}:{hashlib.md5(text.encode()).hexdigest()}"
        
        # Check cache
        cached_embedding = self.cache.get(cache_key)
        if cached_embedding is not None:
            # Record cache hit
            self.debugger.record_cache_access(
                "embedding", 
                cache_key, 
                hit=True, 
                computation_time_ms=500  # Approximate time to compute embedding
            )
            return cached_embedding
            
        # Record cache miss
        self.debugger.record_cache_access("embedding", cache_key, hit=False)
        
        # Compute embedding
        start_time = time.time()
        embedding = self.model.encode(text)
        computation_time = (time.time() - start_time) * 1000
        
        # Store in cache
        self.cache[cache_key] = embedding
        
        return embedding
```

### 4. System Watchdog

The System Watchdog monitors the health of all system components, detecting issues and triggering recovery actions when necessary.

#### Features:
- **Component Heartbeats**: Regularly checks component health
- **Memory Leak Detection**: Monitors memory usage for abnormal patterns
- **Automatic Recovery**: Triggers recovery procedures for failing components
- **Health API**: Provides health status information via API

#### Implementation:

```python
class CodaWatchdog:
    def __init__(self, components, check_interval=30):
        self.components = components
        self.check_interval = check_interval
        self.last_heartbeats = {comp.name: None for comp in components}
        self.health_metrics = defaultdict(list)
        self.running = False
        
    async def start(self):
        self.running = True
        while self.running:
            await self.check_health()
            await asyncio.sleep(self.check_interval)
    
    async def check_health(self):
        """Check health of all components and take recovery actions if needed."""
        for component in self.components:
            try:
                # Request heartbeat from component
                heartbeat = await component.get_heartbeat()
                
                # Update last heartbeat time
                self.last_heartbeats[component.name] = heartbeat
                
                # Check if component is healthy
                if not heartbeat.get("healthy", False):
                    logger.warning(f"Component {component.name} reports unhealthy state")
                    await self.recover_component(component)
                    
                # Record metrics
                self.health_metrics[component.name].append({
                    "timestamp": datetime.now(),
                    "memory_usage": heartbeat.get("memory_usage", 0),
                    "response_time": heartbeat.get("response_time", 0),
                    "error_rate": heartbeat.get("error_rate", 0)
                })
                
            except Exception as e:
                logger.error(f"Failed to get heartbeat from {component.name}: {e}")
                await self.recover_component(component)
    
    async def recover_component(self, component):
        """Attempt to recover a failing component."""
        logger.info(f"Attempting to recover {component.name}")
        
        try:
            # Try gentle restart first
            await component.restart()
            
            # Check if restart was successful
            heartbeat = await component.get_heartbeat()
            if heartbeat.get("healthy", False):
                logger.info(f"Successfully recovered {component.name}")
                return
                
            # If gentle restart failed, try force restart
            logger.warning(f"Gentle restart failed for {component.name}, attempting force restart")
            await component.force_restart()
            
        except Exception as e:
            logger.error(f"Failed to recover {component.name}: {e}")
            # Notify admin or take more drastic measures
    
    def get_health_status(self):
        """Get current health status of all components."""
        status = {
            "overall_health": "healthy",
            "components": {},
            "timestamp": datetime.now().isoformat()
        }
        
        for component in self.components:
            heartbeat = self.last_heartbeats.get(component.name)
            
            if heartbeat is None:
                component_status = "unknown"
            elif heartbeat.get("healthy", False):
                component_status = "healthy"
            else:
                component_status = "unhealthy"
                status["overall_health"] = "degraded"
                
            status["components"][component.name] = {
                "status": component_status,
                "last_heartbeat": heartbeat,
                "metrics": self.health_metrics[component.name][-5:] if self.health_metrics[component.name] else []
            }
            
        return status
```

## Integration with WebSocket API

These debugging tools will be integrated with the WebSocket API to provide real-time debugging information to the dashboard.

### Debug Events

The following debug events will be added to the WebSocket API:

1. **pipeline_stage**: Emitted when a pipeline stage completes
2. **memory_snapshot**: Emitted when a memory snapshot is taken
3. **cache_stats**: Emitted periodically with cache statistics
4. **health_status**: Emitted periodically with system health status

### Debug Commands

The following debug commands will be added to the WebSocket API:

1. **enable_debugging**: Enable or disable debugging features
2. **take_memory_snapshot**: Manually trigger a memory snapshot
3. **get_cache_stats**: Request current cache statistics
4. **get_health_status**: Request current health status

## Dashboard Integration

The debugging tools will be integrated with the dashboard to provide a comprehensive debugging interface.

### Debug Views

1. **Pipeline Visualizer**: Shows the flow of data through the conversation pipeline
2. **Memory Explorer**: Visualizes memory snapshots and evolution
3. **Cache Monitor**: Shows cache performance and recommendations
4. **Health Dashboard**: Displays system health status and metrics

## Conclusion

These debugging tools will significantly enhance the observability and troubleshooting capabilities of Coda Lite. By providing deep insights into the system's behavior, performance, and state, they will make it easier to identify and fix issues, leading to a more robust and reliable system.

The tools are designed to be modular and configurable, allowing developers to enable or disable specific features as needed. They are also designed to have minimal impact on performance when not actively used, ensuring that they don't interfere with normal operation.

Implementation of these tools will begin in Phase 1 (Stability) and continue through Phase 2 (Observability) of our development plan.
