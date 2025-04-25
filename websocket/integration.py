"""
WebSocket integration for Coda.

This module provides integration between Coda's core components and the WebSocket server.
"""

import asyncio
import logging
import time
import threading
import queue
from typing import Dict, Any, Optional, List, Tuple

from .server import CodaWebSocketServer
from .events import EventType

logger = logging.getLogger("coda.websocket.integration")

class CodaWebSocketIntegration:
    """
    Integration between Coda's core components and the WebSocket server.

    This class provides methods to connect Coda's STT, LLM, TTS, and memory
    components to the WebSocket server, allowing clients to receive real-time
    events about Coda's operation.
    """

    def __init__(self, server: CodaWebSocketServer):
        """
        Initialize the WebSocket integration.

        Args:
            server: The WebSocket server to use
        """
        self.server = server
        self.perf_tracker = PerfTracker()

        # Session information
        self.session_id = None
        self.conversation_turn_count = 0

        # Event queue for handling events from non-async threads
        self.event_queue = queue.Queue()

        # Create a dedicated event loop for the event processing thread
        self.event_loop = None

        # Start the event processing thread
        self.event_thread = threading.Thread(target=self._process_event_queue, daemon=True)
        self.event_thread.start()

        logger.info("WebSocket integration initialized")

    def _process_event_queue(self):
        """Process events from the event queue."""
        # Create a new event loop for this thread
        self.event_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.event_loop)

        logger.info("Event processing thread started with dedicated event loop")

        try:
            while True:
                try:
                    # Get the next event from the queue with a timeout
                    # This allows the thread to check for shutdown periodically
                    try:
                        event_type, data, high_priority = self.event_queue.get(timeout=0.5)
                    except queue.Empty:
                        continue

                    # Create a task to push the event
                    async def push_event():
                        try:
                            await self.server.push_event_async(event_type, data, high_priority)
                        except Exception as e:
                            logger.error(f"Error pushing event: {e}", exc_info=True)

                    # Run the task in this thread's event loop
                    try:
                        self.event_loop.run_until_complete(push_event())
                    except Exception as e:
                        logger.error(f"Error running event task: {e}", exc_info=True)

                    # Mark the task as done
                    self.event_queue.task_done()
                except Exception as e:
                    logger.error(f"Error processing event queue: {e}", exc_info=True)
                    time.sleep(0.1)  # Avoid tight loop if there's an error
        finally:
            # Clean up the event loop
            self.event_loop.close()
            logger.info("Event processing thread stopped")

    def start_session(self) -> str:
        """
        Start a new session.

        Returns:
            The session ID
        """
        import uuid

        self.session_id = str(uuid.uuid4())
        self.conversation_turn_count = 0

        # Send conversation start event
        self.event_queue.put((
            EventType.CONVERSATION_START,
            {
                "session_id": self.session_id
            },
            False
        ))

        logger.info(f"Started session {self.session_id}")
        return self.session_id

    def end_session(self) -> None:
        """End the current session."""
        if not self.session_id:
            logger.warning("No active session to end")
            return

        # Send conversation end event
        self.event_queue.put((
            EventType.CONVERSATION_END,
            {
                "session_id": self.session_id,
                "duration_seconds": time.time() - self.perf_tracker.session_start_time,
                "turns_count": self.conversation_turn_count
            },
            False
        ))

        logger.info(f"Ended session {self.session_id}")
        self.session_id = None

    # Keep track of recently sent messages to prevent duplicates
    _recent_messages = {}
    _message_lock = threading.Lock()

    def add_conversation_turn(self, role: str, content: str) -> None:
        """
        Add a conversation turn.

        Args:
            role: The speaker role ("user", "assistant", "system")
            content: The message content
        """
        if not self.session_id:
            logger.warning("No active session for conversation turn")
            return

        # Create a message hash to detect duplicates
        message_hash = f"{role}:{hash(content)}"

        # Check for duplicates with a lock to prevent race conditions
        with self._message_lock:
            # Check if we've seen this message recently (within the last 5 seconds)
            current_time = time.time()
            if message_hash in self._recent_messages:
                last_time = self._recent_messages[message_hash]
                if current_time - last_time < 5.0:  # 5 second window for duplicates
                    logger.warning(f"Duplicate message detected, ignoring: {role}, content_length={len(content)}")
                    return

            # Update the recent messages cache
            self._recent_messages[message_hash] = current_time

            # Clean up old messages (older than 10 seconds)
            self._recent_messages = {k: v for k, v in self._recent_messages.items()
                                    if current_time - v < 10.0}

        # Increment the turn counter and generate a unique ID
        self.conversation_turn_count += 1
        turn_id = f"turn_{self.session_id}_{self.conversation_turn_count}"

        # Send conversation turn event
        logger.info(f"Adding conversation turn: role={role}, turn_id={turn_id}, content_length={len(content)}")

        self.event_queue.put((
            EventType.CONVERSATION_TURN,
            {
                "role": role,
                "content": content,
                "turn_id": turn_id
            },
            True  # Mark as high priority to ensure it's in the replay buffer
        ))

        logger.debug(f"Added conversation turn: {role}, turn_id={turn_id}")

    # STT integration methods

    def stt_start(self, mode: str = "push_to_talk") -> None:
        """
        Signal the start of speech-to-text processing.

        Args:
            mode: The STT mode ("push_to_talk", "continuous", "file")
        """
        self.perf_tracker.mark("stt_start")

        # Send STT start event
        self.event_queue.put((
            EventType.STT_START,
            {
                "mode": mode
            },
            False
        ))

        logger.debug(f"STT started in {mode} mode")

    def stt_interim_result(self, text: str, confidence: float = 0.0) -> None:
        """
        Send an interim STT result.

        Args:
            text: The transcribed text
            confidence: The confidence score (0.0 to 1.0)
        """
        # Send STT interim event
        self.event_queue.put((
            EventType.STT_INTERIM,
            {
                "text": text,
                "confidence": confidence
            },
            False
        ))

        logger.debug(f"STT interim result: {text[:30]}...")

    def stt_result(self, text: str, confidence: float = 0.0, language: Optional[str] = None, duration: Optional[float] = None) -> None:
        """
        Send the final STT result.

        Args:
            text: The transcribed text
            confidence: The confidence score (0.0 to 1.0)
            language: The detected language
            duration: Optional processing duration in seconds (if not provided, calculated from markers)
        """
        self.perf_tracker.mark("stt_end")

        # Use provided duration if available, otherwise calculate from markers
        if duration is None:
            # Try to get the processing duration first (more accurate)
            if "stt_process_duration" in self.perf_tracker.markers:
                duration = self.perf_tracker.markers["stt_process_duration"]
            else:
                # Fall back to total duration including listening time
                duration = self.perf_tracker.get_duration("stt_start", "stt_end")

        # Send STT result event
        self.event_queue.put((
            EventType.STT_RESULT,
            {
                "text": text,
                "confidence": confidence,
                "duration_seconds": duration,
                "language": language
            },
            False
        ))

        logger.debug(f"STT result: {text[:30]}... ({duration:.2f}s)")

        # Add user turn to conversation
        self.add_conversation_turn("user", text)

    def stt_error(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        """
        Signal an STT error.

        Args:
            message: The error message
            details: Additional error details
        """
        self.perf_tracker.mark("stt_error")

        # Send STT error event
        self.event_queue.put((
            EventType.STT_ERROR,
            {
                "message": message,
                "details": details
            },
            False
        ))

        logger.error(f"STT error: {message}")

    # LLM integration methods

    def llm_start(self, model: str, prompt_tokens: int, system_prompt_preview: Optional[str] = None) -> None:
        """
        Signal the start of LLM processing.

        Args:
            model: The LLM model name
            prompt_tokens: The number of tokens in the prompt
            system_prompt_preview: A preview of the system prompt
        """
        self.perf_tracker.mark("llm_start")

        # Send LLM start event
        self.event_queue.put((
            EventType.LLM_START,
            {
                "model": model,
                "prompt_tokens": prompt_tokens,
                "system_prompt_preview": system_prompt_preview
            },
            False
        ))

        logger.debug(f"LLM started with model {model}")

    def llm_token(self, token: str, token_index: int) -> None:
        """
        Send an LLM token.

        Args:
            token: The generated token
            token_index: The token index
        """
        # Send LLM token event
        self.event_queue.put((
            EventType.LLM_TOKEN,
            {
                "token": token,
                "token_index": token_index
            },
            False
        ))

        logger.debug(f"LLM token {token_index}: {token}")

    def llm_result(self, text: str, total_tokens: int, has_tool_calls: bool = False) -> None:
        """
        Send the final LLM result.

        Args:
            text: The generated text
            total_tokens: The total number of tokens (prompt + response)
            has_tool_calls: Whether the response contains tool calls
        """
        self.perf_tracker.mark("llm_end")
        duration = self.perf_tracker.get_duration("llm_start", "llm_end")

        # Send LLM result event
        self.event_queue.put((
            EventType.LLM_RESULT,
            {
                "text": text,
                "total_tokens": total_tokens,
                "duration_seconds": duration,
                "has_tool_calls": has_tool_calls
            },
            False
        ))

        logger.debug(f"LLM result: {text[:30]}... ({duration:.2f}s)")

        # Add assistant turn to conversation
        self.add_conversation_turn("assistant", text)

    def llm_error(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        """
        Signal an LLM error.

        Args:
            message: The error message
            details: Additional error details
        """
        self.perf_tracker.mark("llm_error")

        # Send LLM error event
        self.event_queue.put((
            EventType.LLM_ERROR,
            {
                "message": message,
                "details": details
            },
            False
        ))

        logger.error(f"LLM error: {message}")

    # TTS integration methods

    def tts_start(self, text: str, voice: str, provider: str) -> None:
        """
        Signal the start of TTS processing.

        Args:
            text: The text to synthesize
            voice: The voice to use
            provider: The TTS provider
        """
        self.perf_tracker.mark("tts_start")

        # Send TTS start event
        self.event_queue.put((
            EventType.TTS_START,
            {
                "text": text,
                "voice": voice,
                "provider": provider
            },
            False
        ))

        logger.debug(f"TTS started with voice {voice} ({provider})")

    def tts_progress(self, percent_complete: float) -> None:
        """
        Send a TTS progress update.

        Args:
            percent_complete: The percentage complete (0.0 to 100.0)
        """
        # Send TTS progress event
        self.event_queue.put((
            EventType.TTS_PROGRESS,
            {
                "percent_complete": percent_complete
            },
            False
        ))

        logger.debug(f"TTS progress: {percent_complete:.1f}%")

    def tts_result(self, audio_duration_seconds: float, char_count: int) -> None:
        """
        Send the final TTS result.

        Args:
            audio_duration_seconds: The duration of the generated audio
            char_count: The number of characters in the input text
        """
        self.perf_tracker.mark("tts_end")

        # Try to get the synthesis duration first (more accurate)
        if "tts_synthesis_duration" in self.perf_tracker.markers:
            duration = self.perf_tracker.markers["tts_synthesis_duration"]
        else:
            # Fall back to total duration including playback time
            duration = self.perf_tracker.get_duration("tts_start", "tts_end")

        # Send TTS result event
        self.event_queue.put((
            EventType.TTS_RESULT,
            {
                "duration_seconds": duration,
                "audio_duration_seconds": audio_duration_seconds,
                "char_count": char_count
            },
            False
        ))

        logger.debug(f"TTS result: {audio_duration_seconds:.2f}s audio ({duration:.2f}s processing)")

        # Send latency trace
        self._send_latency_trace()

    def tts_error(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        """
        Signal a TTS error.

        Args:
            message: The error message
            details: Additional error details
        """
        self.perf_tracker.mark("tts_error")

        # Send TTS error event
        self.event_queue.put((
            EventType.TTS_ERROR,
            {
                "message": message,
                "details": details
            },
            False
        ))

        logger.error(f"TTS error: {message}")

        # Send latency trace
        self._send_latency_trace()

    def tts_status(self, status: str, details: Optional[Dict[str, Any]] = None) -> None:
        """
        Signal a TTS status change.

        Args:
            status: The status ("loaded", "unloaded", "switching")
            details: Additional status details
        """
        # Send TTS status event
        self.event_queue.put((
            EventType.TTS_STATUS,
            {
                "status": status,
                "details": details
            },
            False
        ))

        logger.debug(f"TTS status: {status}")

    def tts_stop(self, reason: Optional[str] = "user_interrupt") -> None:
        """
        Signal to stop TTS playback.

        Args:
            reason: The reason for stopping TTS playback
        """
        self.perf_tracker.mark("tts_stop")

        # Send TTS stop event
        self.event_queue.put((
            EventType.TTS_STOP,
            {
                "reason": reason
            },
            True  # high_priority
        ))

        logger.debug(f"TTS stopped: {reason}")

    # Memory integration methods

    def memory_store(self, content: str, memory_type: str, importance: float, memory_id: str) -> None:
        """
        Signal that a memory has been stored.

        Args:
            content: The memory content
            memory_type: The memory type
            importance: The importance score
            memory_id: The memory ID
        """
        # Create a preview of the content
        content_preview = content[:100] + "..." if len(content) > 100 else content

        logger.info(f"Storing memory: id={memory_id}, type={memory_type}, importance={importance}")

        # Send memory store event
        self.event_queue.put((
            EventType.MEMORY_STORE,
            {
                "content_preview": content_preview,
                "memory_type": memory_type,
                "importance": importance,
                "memory_id": memory_id,
                "timestamp": time.time()  # Add timestamp for proper display in UI
            },
            True  # high_priority
        ))

        logger.debug(f"Memory stored: id={memory_id}, preview={content_preview[:30]}...")

    def memory_retrieve(self, query: str, results: List[Dict[str, Any]]) -> None:
        """
        Signal that memories have been retrieved.

        Args:
            query: The search query
            results: The search results
        """
        # Get the top result preview
        top_result_preview = None
        if results:
            content = results[0].get("content", "")
            top_result_preview = content[:100] + "..." if len(content) > 100 else content

        # Format results for transmission
        formatted_results = []
        for result in results:
            # Create a copy to avoid modifying the original
            formatted_result = {
                "id": result.get("id", f"mem_{int(time.time())}_{len(formatted_results)}"),
                "content": result.get("content", ""),
                "score": result.get("score", 0.5),
                "metadata": result.get("metadata", {})
            }
            formatted_results.append(formatted_result)

        # Send memory retrieve event
        self.event_queue.put((
            EventType.MEMORY_RETRIEVE,
            {
                "query": query,
                "results_count": len(results),
                "top_result_preview": top_result_preview,
                "results": formatted_results  # Include the full results
            },
            True  # Mark as high priority to ensure it's in the replay buffer
        ))

        logger.debug(f"Memory retrieved: {len(results)} results for query '{query}'")

    def memory_update(self, memory_id: str, field: str, old_value: Any, new_value: Any) -> None:
        """
        Signal that a memory has been updated.

        Args:
            memory_id: The memory ID
            field: The updated field
            old_value: The old value
            new_value: The new value
        """
        # Send memory update event
        self.event_queue.put((
            EventType.MEMORY_UPDATE,
            {
                "memory_id": memory_id,
                "field": field,
                "old_value": old_value,
                "new_value": new_value
            },
            False
        ))

        logger.debug(f"Memory updated: {memory_id} {field}")

    # Tool integration methods

    def tool_call(self, tool_name: str, parameters: Dict[str, Any]) -> None:
        """
        Signal that a tool is being called.

        Args:
            tool_name: The tool name
            parameters: The tool parameters
        """
        self.perf_tracker.mark("tool_start")

        # Send tool call event
        self.event_queue.put((
            EventType.TOOL_CALL,
            {
                "tool_name": tool_name,
                "parameters": parameters
            },
            False
        ))

        logger.debug(f"Tool call: {tool_name}")

    def tool_result(self, tool_name: str, result: Any) -> None:
        """
        Signal that a tool has returned a result.

        Args:
            tool_name: The tool name
            result: The tool result
        """
        self.perf_tracker.mark("tool_end")
        duration = self.perf_tracker.get_duration("tool_start", "tool_end")

        # Create a preview of the result
        result_str = str(result)
        result_preview = result_str[:100] + "..." if len(result_str) > 100 else result_str

        # Send tool result event
        self.event_queue.put((
            EventType.TOOL_RESULT,
            {
                "tool_name": tool_name,
                "result_preview": result_preview,
                "duration_seconds": duration
            },
            False
        ))

        logger.debug(f"Tool result: {tool_name} ({duration:.2f}s)")

    def tool_error(self, tool_name: str, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        """
        Signal a tool error.

        Args:
            tool_name: The tool name
            message: The error message
            details: Additional error details
        """
        self.perf_tracker.mark("tool_error")

        # Send tool error event
        self.event_queue.put((
            EventType.TOOL_ERROR,
            {
                "tool_name": tool_name,
                "message": message,
                "details": details
            },
            False
        ))

        logger.error(f"Tool error: {tool_name} - {message}")

    # System integration methods

    def system_info(self, info: Dict[str, Any]) -> None:
        """
        Send system information.

        Args:
            info: The system information
        """
        # Send system info event
        self.event_queue.put((
            EventType.SYSTEM_INFO,
            info,
            True  # high_priority
        ))

        logger.debug("System info sent")

    def system_error(self, level: str, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        """
        Send a system error.

        Args:
            level: The error level ("warning", "error", "critical")
            message: The error message
            details: Additional error details
        """
        # Send system error event
        self.event_queue.put((
            EventType.SYSTEM_ERROR,
            {
                "level": level,
                "message": message,
                "details": details
            },
            True  # high_priority
        ))

        logger.error(f"System error ({level}): {message}")

    def system_metrics(self, memory_mb: float, cpu_percent: float,
                      gpu_vram_mb: Optional[float] = None,
                      uptime_seconds: Optional[float] = None) -> None:
        """
        Send system metrics.

        Args:
            memory_mb: Memory usage in MB
            cpu_percent: CPU usage percentage
            gpu_vram_mb: GPU VRAM usage in MB
            uptime_seconds: System uptime in seconds
        """
        # Calculate uptime if not provided
        if uptime_seconds is None:
            uptime_seconds = time.time() - self.perf_tracker.session_start_time

        logger.info(f"Sending system metrics: Memory={memory_mb:.1f}MB, CPU={cpu_percent:.1f}%, GPU VRAM={gpu_vram_mb or 0:.1f}MB")

        # Send system metrics event
        self.event_queue.put((
            EventType.SYSTEM_METRICS,
            {
                "memory_mb": float(memory_mb),
                "cpu_percent": float(cpu_percent),
                "gpu_vram_mb": float(gpu_vram_mb) if gpu_vram_mb is not None else 0.0,
                "uptime_seconds": float(uptime_seconds)
            },
            True  # Mark as high priority to ensure it's in the replay buffer
        ))

        logger.debug(f"System metrics sent: {memory_mb:.1f}MB, {cpu_percent:.1f}% CPU")

    # Helper methods

    def _send_latency_trace(self) -> None:
        """Send a latency trace event with timing information."""
        # Get processing times (excluding audio recording/playback)
        # Try to use component-specific markers first, then fall back to standard markers
        if "stt_process_duration" in self.perf_tracker.markers:
            stt_seconds = self.perf_tracker.markers["stt_process_duration"]
        else:
            stt_seconds = self.perf_tracker.get_duration("stt_start", "stt_end")

        llm_seconds = self.perf_tracker.get_duration("llm_start", "llm_end")

        if "tts_synthesis_duration" in self.perf_tracker.markers:
            tts_seconds = self.perf_tracker.markers["tts_synthesis_duration"]
        else:
            tts_seconds = self.perf_tracker.get_duration("tts_start", "tts_end")

        tool_seconds = self.perf_tracker.get_duration("tool_start", "tool_end")
        memory_seconds = 0  # Add memory operation timing if available

        # Calculate total processing time (excluding audio playback/recording)
        total_seconds = stt_seconds + llm_seconds + tts_seconds
        if tool_seconds > 0:
            total_seconds += tool_seconds
        if memory_seconds > 0:
            total_seconds += memory_seconds

        # Get audio durations if available
        stt_audio_duration = self.perf_tracker.markers.get("stt_audio_duration", 0)
        tts_audio_duration = self.perf_tracker.markers.get("tts_audio_duration", 0)

        # Calculate total interaction time (processing + audio)
        total_interaction_seconds = total_seconds + stt_audio_duration + tts_audio_duration

        logger.info(f"Sending latency trace: STT={stt_seconds:.2f}s, LLM={llm_seconds:.2f}s, TTS={tts_seconds:.2f}s, Total={total_seconds:.2f}s")

        # Send latency trace event with clear separation between processing and audio times
        self.event_queue.put((
            EventType.LATENCY_TRACE,
            {
                "stt_seconds": stt_seconds,  # Processing time only
                "llm_seconds": llm_seconds,
                "tts_seconds": tts_seconds,  # Synthesis time only (not playback)
                "total_processing_seconds": total_seconds,  # Total processing time
                "total_seconds": total_seconds,  # Keep for backward compatibility
                "tool_seconds": tool_seconds if tool_seconds > 0 else 0,
                "memory_seconds": memory_seconds,
                "stt_audio_duration": stt_audio_duration,  # Actual audio recording duration
                "tts_audio_duration": tts_audio_duration,  # Actual audio playback duration
                "total_interaction_seconds": total_interaction_seconds  # Total time including audio
            },
            True  # Mark as high priority to ensure it's in the replay buffer
        ))

        logger.debug(f"Latency trace sent: STT={stt_seconds:.2f}s, LLM={llm_seconds:.2f}s, TTS={tts_seconds:.2f}s, Total={total_seconds:.2f}s")


class PerfTracker:
    """
    Performance tracker for measuring latency.

    This class provides methods to mark points in time and calculate durations
    between those points.
    """

    def __init__(self):
        """Initialize the performance tracker."""
        self.markers = {}
        self.session_start_time = time.time()

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

    def mark_component(self, component: str, operation: str, start: bool = True) -> float:
        """
        Mark a component-specific operation start or end.

        Args:
            component: The component name (e.g., "stt", "llm", "tts")
            operation: The operation name (e.g., "process", "generate", "synthesize")
            start: True if this is the start of the operation, False if it's the end

        Returns:
            The current time
        """
        marker_name = f"{component}.{operation}.{'start' if start else 'end'}"
        return self.mark(marker_name)

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

    def get_component_duration(self, component: str, operation: str) -> float:
        """
        Get the duration of a component-specific operation.

        Args:
            component: The component name (e.g., "stt", "llm", "tts")
            operation: The operation name (e.g., "process", "generate", "synthesize")

        Returns:
            The duration in seconds, or 0 if either marker is missing
        """
        start_marker = f"{component}.{operation}.start"
        end_marker = f"{component}.{operation}.end"
        return self.get_duration(start_marker, end_marker)

    def reset(self) -> None:
        """Reset all markers."""
        self.markers = {}
        self.session_start_time = time.time()
