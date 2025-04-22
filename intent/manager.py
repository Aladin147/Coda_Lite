"""
Intent manager for Coda Lite.

This module provides a manager class that integrates intent routing with the main application.
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from .intent_router import IntentRouter, IntentType
from .handlers import IntentHandlers

logger = logging.getLogger("coda.intent.manager")

class IntentManager:
    """
    Manager for intent routing and handling.
    
    This class:
    - Initializes and configures the intent router and handlers
    - Processes user input through the intent pipeline
    - Integrates with memory, tools, and personality systems
    """
    
    def __init__(self, memory_manager=None, tool_router=None, personality_manager=None):
        """
        Initialize the intent manager.
        
        Args:
            memory_manager: Memory manager for accessing memory
            tool_router: Tool router for executing tools
            personality_manager: Personality manager for adjusting personality
        """
        self.memory_manager = memory_manager
        self.tool_router = tool_router
        self.personality_manager = personality_manager
        
        # Initialize intent router
        self.router = IntentRouter()
        
        # Initialize intent handlers
        self.handlers = IntentHandlers(
            memory_manager=memory_manager,
            tool_router=tool_router,
            personality_manager=personality_manager
        )
        
        # Register handlers
        self._register_handlers()
        
        logger.info("Intent manager initialized")
    
    def _register_handlers(self) -> None:
        """Register all intent handlers with the router."""
        handlers = self.handlers.get_all_handlers()
        
        for intent_type, handler_func in handlers.items():
            self.router.register_intent_handler(intent_type, handler_func)
        
        logger.info(f"Registered {len(handlers)} intent handlers")
    
    def process_input(self, user_input: str) -> Dict[str, Any]:
        """
        Process user input through the intent pipeline.
        
        Args:
            user_input: User input text
            
        Returns:
            Processing result
        """
        logger.info(f"Processing user input: {user_input}")
        
        # Route the intent
        result = self.router.route_intent(user_input)
        
        # Update context based on intent
        self._update_context(result)
        
        return result
    
    def _update_context(self, result: Dict[str, Any]) -> None:
        """
        Update context based on intent processing result.
        
        Args:
            result: Intent processing result
        """
        intent_type = result.get("intent_type")
        
        # Update personality context based on intent type
        if self.personality_manager and hasattr(self.personality_manager, 'current_context'):
            context_update = {}
            
            if intent_type == IntentType.INFORMATION_REQUEST:
                context_update["type"] = "information_request"
            elif intent_type == IntentType.MEMORY_RECALL:
                context_update["type"] = "memory_recall"
            elif intent_type == IntentType.EXTERNAL_ACTION:
                context_update["type"] = "external_action"
            elif intent_type == IntentType.TOOL_USE:
                context_update["type"] = "tool_use"
            
            # Only update if we have a specific context type
            if context_update:
                try:
                    # Update the current context
                    self.personality_manager.current_context.update(context_update)
                    logger.info(f"Updated personality context: {context_update}")
                except Exception as e:
                    logger.error(f"Error updating personality context: {e}")
    
    def get_intent_history(self, limit: int = None) -> List[Dict[str, Any]]:
        """
        Get intent history.
        
        Args:
            limit: Maximum number of history items to return
            
        Returns:
            List of intent history items
        """
        return self.router.get_intent_history(limit)
    
    def get_intent_distribution(self) -> Dict[IntentType, int]:
        """
        Get distribution of intents in history.
        
        Returns:
            Dictionary mapping intent types to counts
        """
        return self.router.get_intent_distribution()
    
    def clear_history(self) -> None:
        """Clear intent history."""
        self.router.clear_history()
        logger.info("Cleared intent history")
    
    def set_debug_mode(self, enabled: bool) -> None:
        """
        Set debug mode.
        
        Args:
            enabled: Whether debug mode should be enabled
        """
        self.handlers.debug_mode = enabled
        logger.info(f"Debug mode {'enabled' if enabled else 'disabled'}")
    
    def get_debug_mode(self) -> bool:
        """
        Get debug mode status.
        
        Returns:
            Whether debug mode is enabled
        """
        return self.handlers.debug_mode
