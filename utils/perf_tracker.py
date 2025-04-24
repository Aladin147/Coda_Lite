"""
Performance tracking utilities for Coda Lite.

This module provides utilities for tracking performance metrics throughout the system,
including timing, memory usage, CPU usage, and GPU usage.
"""

import os
import time
import logging
import threading
import platform
from typing import Dict, List, Optional, Any, Union, Callable
from datetime import datetime

logger = logging.getLogger("coda.utils.perf_tracker")

# Try to import optional dependencies
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    logger.warning("psutil not available, system resource monitoring will be limited")
    PSUTIL_AVAILABLE = False

try:
    import GPUtil
    GPUTIL_AVAILABLE = True
except ImportError:
    logger.warning("GPUtil not available, GPU monitoring will be disabled")
    GPUTIL_AVAILABLE = False

try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    logger.warning("torch not available, CUDA memory monitoring will be disabled")
    TORCH_AVAILABLE = False


class PerfTracker:
    """
    Performance tracker for measuring latency and system resources.

    This class provides methods to mark points in time, calculate durations,
    and monitor system resources like CPU, memory, and GPU usage.
    """

    def __init__(self,
                 enable_system_monitoring: bool = True,
                 monitoring_interval: float = 5.0,
                 event_callback: Optional[Callable[[str, Dict[str, Any]], None]] = None):
        """
        Initialize the performance tracker.

        Args:
            enable_system_monitoring: Whether to enable system resource monitoring
            monitoring_interval: Interval in seconds for system monitoring
            event_callback: Callback function for performance events
        """
        # Initialize markers
        self.markers = {}
        self.session_start_time = time.time()
        self.component_timings = {}
        self.operation_counts = {}

        # System monitoring
        self.enable_system_monitoring = enable_system_monitoring
        self.monitoring_interval = monitoring_interval
        self.event_callback = event_callback
        self.monitoring_thread = None
        self.running = False

        # System info
        self.system_info = self._get_system_info()

        # Start monitoring if enabled
        if self.enable_system_monitoring:
            self.start_monitoring()

        logger.info("PerfTracker initialized")

    def _get_system_info(self) -> Dict[str, Any]:
        """
        Get system information.

        Returns:
            Dictionary with system information
        """
        info = {
            "platform": platform.platform(),
            "python_version": platform.python_version(),
            "processor": platform.processor(),
            "cpu_count": os.cpu_count()
        }

        # Add psutil info if available
        if PSUTIL_AVAILABLE:
            memory = psutil.virtual_memory()
            info.update({
                "total_memory_mb": memory.total / (1024 * 1024),
                "cpu_freq_mhz": psutil.cpu_freq().current if psutil.cpu_freq() else None
            })

        # Add GPU info if available
        if GPUTIL_AVAILABLE:
            try:
                gpus = GPUtil.getGPUs()
                if gpus:
                    gpu = gpus[0]  # Use the first GPU
                    info.update({
                        "gpu_name": gpu.name,
                        "gpu_driver": gpu.driver,
                        "gpu_memory_total_mb": gpu.memoryTotal
                    })
            except Exception as e:
                logger.warning(f"Error getting GPU info: {e}")

        # Add CUDA info if available
        if TORCH_AVAILABLE and torch.cuda.is_available():
            info.update({
                "cuda_version": torch.version.cuda,
                "cuda_device_count": torch.cuda.device_count(),
                "cuda_device_name": torch.cuda.get_device_name(0) if torch.cuda.device_count() > 0 else None
            })

        return info

    def get_system_info(self) -> Dict[str, Any]:
        """
        Get system information.

        Returns:
            Dictionary with system information
        """
        return self.system_info

    def mark(self, name: str) -> float:
        """
        Mark a point in time.

        Args:
            name: The marker name

        Returns:
            The current time
        """
        current_time = time.time()
        self.markers[name] = current_time
        return current_time

    def mark_component(self, component: str, operation: str, start: bool = True) -> None:
        """
        Mark the start or end of a component operation.

        Args:
            component: The component name (e.g., "stt", "llm", "tts")
            operation: The operation name (e.g., "process", "initialize")
            start: Whether this is the start (True) or end (False) of the operation
        """
        marker_name = f"{component}.{operation}.{'start' if start else 'end'}"
        self.mark(marker_name)

        # Track operation counts
        if start:
            if component not in self.operation_counts:
                self.operation_counts[component] = {}

            if operation not in self.operation_counts[component]:
                self.operation_counts[component][operation] = 0

            self.operation_counts[component][operation] += 1

        # Calculate duration if this is the end marker
        if not start:
            start_marker = f"{component}.{operation}.start"
            if start_marker in self.markers:
                duration = self.get_duration(start_marker, marker_name)

                # Store the timing
                if component not in self.component_timings:
                    self.component_timings[component] = {}

                if operation not in self.component_timings[component]:
                    self.component_timings[component][operation] = []

                self.component_timings[component][operation].append(duration)

                # Log the timing
                logger.debug(f"{component}.{operation} took {duration:.3f}s")

                # Send event if callback is provided
                if self.event_callback:
                    self.event_callback("component_timing", {
                        "component": component,
                        "operation": operation,
                        "duration_seconds": duration
                    })

    def get_duration(self, start_marker: str, end_marker: str) -> float:
        """
        Get the duration between two markers.

        Args:
            start_marker: The start marker name
            end_marker: The end marker name

        Returns:
            The duration in seconds, or 0 if either marker is missing
        """
        if start_marker not in self.markers or end_marker not in self.markers:
            return 0.0

        return self.markers[end_marker] - self.markers[start_marker]

    def get_component_stats(self, component: Optional[str] = None) -> Dict[str, Any]:
        """
        Get statistics for component operations.

        Args:
            component: The component name, or None for all components

        Returns:
            Dictionary with component statistics
        """
        stats = {}

        # Get all components or just the specified one
        components = [component] if component else list(self.component_timings.keys())

        for comp in components:
            if comp in self.component_timings:
                comp_stats = {}

                for operation, timings in self.component_timings[comp].items():
                    if timings:
                        avg_time = sum(timings) / len(timings)
                        max_time = max(timings)
                        min_time = min(timings)
                        count = self.operation_counts.get(comp, {}).get(operation, 0)

                        comp_stats[operation] = {
                            "avg_seconds": avg_time,
                            "max_seconds": max_time,
                            "min_seconds": min_time,
                            "count": count,
                            "total_seconds": sum(timings)
                        }

                stats[comp] = comp_stats

        return stats

    def get_system_metrics(self) -> Dict[str, Any]:
        """
        Get current system metrics.

        Returns:
            Dictionary with system metrics
        """
        metrics = {
            "timestamp": time.time(),
            "uptime_seconds": time.time() - self.session_start_time
        }

        # Add CPU and memory metrics if psutil is available
        if PSUTIL_AVAILABLE:
            try:
                # CPU usage
                metrics["cpu_percent"] = psutil.cpu_percent(interval=0.1)

                # Memory usage
                memory = psutil.virtual_memory()
                metrics["memory_total_mb"] = memory.total / (1024 * 1024)
                metrics["memory_used_mb"] = memory.used / (1024 * 1024)
                metrics["memory_percent"] = memory.percent

                # Process-specific metrics
                process = psutil.Process(os.getpid())
                metrics["process_cpu_percent"] = process.cpu_percent(interval=0.1)
                metrics["process_memory_mb"] = process.memory_info().rss / (1024 * 1024)
                metrics["process_threads"] = process.num_threads()
            except Exception as e:
                logger.warning(f"Error getting system metrics: {e}")

        # Add GPU metrics if GPUtil is available
        if GPUTIL_AVAILABLE:
            try:
                gpus = GPUtil.getGPUs()
                if gpus:
                    gpu = gpus[0]  # Use the first GPU
                    metrics["gpu_load_percent"] = gpu.load * 100
                    metrics["gpu_memory_used_mb"] = gpu.memoryUsed
                    metrics["gpu_memory_total_mb"] = gpu.memoryTotal
                    metrics["gpu_memory_percent"] = (gpu.memoryUsed / gpu.memoryTotal) * 100
            except Exception as e:
                logger.warning(f"Error getting GPU metrics: {e}")

        # Add CUDA metrics if torch is available
        if TORCH_AVAILABLE and torch.cuda.is_available():
            try:
                metrics["cuda_memory_allocated_mb"] = torch.cuda.memory_allocated() / (1024 * 1024)
                metrics["cuda_memory_reserved_mb"] = torch.cuda.memory_reserved() / (1024 * 1024)
                metrics["cuda_max_memory_allocated_mb"] = torch.cuda.max_memory_allocated() / (1024 * 1024)
            except Exception as e:
                logger.warning(f"Error getting CUDA metrics: {e}")

        return metrics

    def _monitoring_loop(self) -> None:
        """Background thread for system monitoring."""
        logger.info("System monitoring started")

        while self.running:
            try:
                # Get system metrics
                metrics = self.get_system_metrics()

                # Log metrics
                logger.debug(f"System metrics: CPU={metrics.get('cpu_percent', 'N/A')}%, "
                            f"Memory={metrics.get('memory_percent', 'N/A')}%, "
                            f"GPU={metrics.get('gpu_memory_percent', 'N/A')}%")

                # Send event if callback is provided
                if self.event_callback:
                    self.event_callback("system_metrics", metrics)

            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")

            # Sleep for the monitoring interval
            time.sleep(self.monitoring_interval)

        logger.info("System monitoring stopped")

    def start_monitoring(self) -> None:
        """Start system monitoring."""
        if self.monitoring_thread is not None and self.monitoring_thread.is_alive():
            logger.warning("Monitoring already running")
            return

        self.running = True
        self.monitoring_thread = threading.Thread(
            target=self._monitoring_loop,
            daemon=True
        )
        self.monitoring_thread.start()
        logger.info("Started system monitoring")

    def stop_monitoring(self) -> None:
        """Stop system monitoring."""
        self.running = False
        if self.monitoring_thread is not None:
            self.monitoring_thread.join(timeout=2.0)
            logger.info("Stopped system monitoring")

    def reset(self) -> None:
        """Reset all markers and statistics."""
        self.markers = {}
        self.component_timings = {}
        self.operation_counts = {}
        self.session_start_time = time.time()
        logger.info("Reset performance tracker")

    def get_latency_trace(self) -> Dict[str, Any]:
        """
        Get a latency trace with timing information for the main components.

        Returns:
            Dictionary with latency information
        """
        # Get durations for main components
        # For STT, we want the processing time, not the listening time
        stt_seconds = self.get_duration("stt.process.start", "stt.process.end")
        if stt_seconds == 0:  # Fallback to old markers if component markers not available
            stt_seconds = self.get_duration("stt_start", "stt_end")

        # For LLM, we want the generation time
        llm_seconds = self.get_duration("llm.generate_response.start", "llm.generate_response.end")
        if llm_seconds == 0:  # Fallback to old markers
            llm_seconds = self.get_duration("llm_start", "llm_end")

        # For TTS, we want the synthesis time, not the playback time
        tts_seconds = self.get_duration("tts.synthesize.start", "tts.synthesize.end")
        if tts_seconds == 0:  # Fallback to old markers
            tts_seconds = self.get_duration("tts_start", "tts_end")

        # Get other component times
        tool_seconds = self.get_duration("tool_start", "tool_end")
        memory_seconds = self.get_duration("memory_start", "memory_end")

        # Get audio durations if available
        tts_audio_duration = self.markers.get("tts_audio_duration", 0)
        stt_audio_duration = self.markers.get("stt_audio_duration", 0)

        # Calculate total processing time (excluding audio playback/recording)
        total_seconds = stt_seconds + llm_seconds + tts_seconds
        if tool_seconds > 0:
            total_seconds += tool_seconds
        if memory_seconds > 0:
            total_seconds += memory_seconds

        # Create trace
        trace = {
            "timestamp": time.time(),
            "stt_seconds": stt_seconds,
            "llm_seconds": llm_seconds,
            "tts_seconds": tts_seconds,
            "total_seconds": total_seconds,
            "tts_audio_duration": tts_audio_duration,
            "stt_audio_duration": stt_audio_duration
        }

        # Add optional components
        if tool_seconds > 0:
            trace["tool_seconds"] = tool_seconds
        if memory_seconds > 0:
            trace["memory_seconds"] = memory_seconds

        return trace


class PerformanceMonitor:
    """
    System-wide performance monitoring for Coda.

    This class provides a singleton instance for tracking performance
    across the entire system.
    """

    _instance = None

    @classmethod
    def get_instance(cls,
                    enable_system_monitoring: bool = True,
                    monitoring_interval: float = 5.0,
                    event_callback: Optional[Callable[[str, Dict[str, Any]], None]] = None) -> PerfTracker:
        """
        Get the singleton instance of the performance tracker.

        Args:
            enable_system_monitoring: Whether to enable system resource monitoring
            monitoring_interval: Interval in seconds for system monitoring
            event_callback: Callback function for performance events

        Returns:
            The singleton PerfTracker instance
        """
        if cls._instance is None:
            cls._instance = PerfTracker(
                enable_system_monitoring=enable_system_monitoring,
                monitoring_interval=monitoring_interval,
                event_callback=event_callback
            )

        return cls._instance

    @classmethod
    def reset_instance(cls) -> None:
        """Reset the singleton instance."""
        if cls._instance is not None:
            cls._instance.stop_monitoring()
            cls._instance = None
