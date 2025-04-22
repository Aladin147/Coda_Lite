"""
Personality module for Coda Lite.

This module provides personality management for Coda Lite, including:
- Basic personality traits and interaction styles
- Enhanced personality with context-aware traits
- Adaptive tone switching
- Personality quirks and signature behaviors
- Advanced personality features with behavioral conditioning
- Topic awareness and session management
- Configurable personality parameters
- Personal lore with backstory and preferences
"""

from .personality_loader import PersonalityLoader
from .enhanced_personality_loader import EnhancedPersonalityLoader
from .parameters import PersonalityParameters
from .behavioral_conditioning import BehavioralConditioner
from .topic_awareness import TopicAwareness
from .session_manager import SessionManager
from .personal_lore import PersonalLoreManager
from .advanced_personality_manager import AdvancedPersonalityManager

__all__ = [
    "PersonalityLoader",
    "EnhancedPersonalityLoader",
    "PersonalityParameters",
    "BehavioralConditioner",
    "TopicAwareness",
    "SessionManager",
    "PersonalLoreManager",
    "AdvancedPersonalityManager"
]
