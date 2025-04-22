"""
Feedback module for Coda Lite.

This module provides feedback collection and processing capabilities for Coda Lite, including:
- Feedback hooks for different intents
- Feedback storage and analysis
- Feedback-based learning
"""

from .feedback_manager import FeedbackManager, FeedbackType, FeedbackPrompt

__all__ = ["FeedbackManager", "FeedbackType", "FeedbackPrompt"]
