"""
Intent handlers for Coda Lite.

This module provides handler functions for different intent types.
"""

import logging
import random
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from .intent_router import IntentType

logger = logging.getLogger("coda.intent.handlers")

class IntentHandlers:
    """
    Handlers for different intent types.

    This class:
    - Provides handler functions for different intent types
    - Integrates with memory, tools, and personality systems
    """

    def __init__(self, memory_manager=None, tool_router=None, personality_manager=None):
        """
        Initialize intent handlers.

        Args:
            memory_manager: Memory manager for accessing memory
            tool_router: Tool router for executing tools
            personality_manager: Personality manager for adjusting personality
        """
        self.memory_manager = memory_manager
        self.tool_router = tool_router
        self.personality_manager = personality_manager

        # Debug mode
        self.debug_mode = False

        logger.info("Intent handlers initialized")

    def handle_information_request(self, user_input: str, entities: Dict[str, Any], metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle information request intent.

        Args:
            user_input: User input text
            entities: Extracted entities
            metadata: Intent metadata

        Returns:
            Handler result
        """
        logger.info(f"Handling information request: {user_input}")

        # For information requests, we'll let the LLM handle it directly
        return {
            "action": "llm_response",
            "message": "Processing information request",
            "debug": self._get_debug_info(user_input, entities, metadata) if self.debug_mode else None
        }

    def handle_memory_recall(self, user_input: str, entities: Dict[str, Any], metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle memory recall intent.

        Args:
            user_input: User input text
            entities: Extracted entities
            metadata: Intent metadata

        Returns:
            Handler result
        """
        logger.info(f"Handling memory recall: {user_input}")

        recall_subject = entities.get("recall_subject", "")

        if not recall_subject:
            return {
                "action": "llm_response",
                "message": "I'm not sure what you want me to recall.",
                "debug": self._get_debug_info(user_input, entities, metadata) if self.debug_mode else None
            }

        # If we have a memory manager, search for relevant memories
        if self.memory_manager and hasattr(self.memory_manager, 'search_memories'):
            try:
                memories = self.memory_manager.search_memories(recall_subject, limit=3)

                if memories and len(memories) > 0:
                    return {
                        "action": "memory_recall",
                        "recall_subject": recall_subject,
                        "memories": memories,
                        "message": f"Found {len(memories)} memories related to '{recall_subject}'",
                        "debug": self._get_debug_info(user_input, entities, metadata) if self.debug_mode else None
                    }
                else:
                    return {
                        "action": "memory_recall",
                        "recall_subject": recall_subject,
                        "memories": [],
                        "message": f"I don't have any specific memories about '{recall_subject}'",
                        "debug": self._get_debug_info(user_input, entities, metadata) if self.debug_mode else None
                    }
            except Exception as e:
                logger.error(f"Error searching memories: {e}")
                return {
                    "action": "error",
                    "message": f"I encountered an error while trying to recall information about '{recall_subject}'",
                    "error": str(e),
                    "debug": self._get_debug_info(user_input, entities, metadata) if self.debug_mode else None
                }

        # If no memory manager, let the LLM handle it
        return {
            "action": "llm_response",
            "message": "Processing memory recall request",
            "debug": self._get_debug_info(user_input, entities, metadata) if self.debug_mode else None
        }

    def handle_memory_store(self, user_input: str, entities: Dict[str, Any], metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle memory store intent.

        Args:
            user_input: User input text
            entities: Extracted entities
            metadata: Intent metadata

        Returns:
            Handler result
        """
        logger.info(f"Handling memory store: {user_input}")

        store_content = entities.get("store_content", "")

        if not store_content:
            return {
                "action": "llm_response",
                "message": "I'm not sure what you want me to remember.",
                "debug": self._get_debug_info(user_input, entities, metadata) if self.debug_mode else None
            }

        # If we have a memory manager, store the memory
        if self.memory_manager and hasattr(self.memory_manager, 'add_fact'):
            try:
                memory_id = self.memory_manager.add_fact(store_content)

                return {
                    "action": "memory_store",
                    "store_content": store_content,
                    "memory_id": memory_id,
                    "message": f"I've remembered that {store_content}",
                    "debug": self._get_debug_info(user_input, entities, metadata) if self.debug_mode else None
                }
            except Exception as e:
                logger.error(f"Error storing memory: {e}")
                return {
                    "action": "error",
                    "message": f"I encountered an error while trying to remember that information",
                    "error": str(e),
                    "debug": self._get_debug_info(user_input, entities, metadata) if self.debug_mode else None
                }

        # If no memory manager, let the LLM handle it
        return {
            "action": "llm_response",
            "message": "I'll try to remember that.",
            "debug": self._get_debug_info(user_input, entities, metadata) if self.debug_mode else None
        }

    def handle_external_action(self, user_input: str, entities: Dict[str, Any], metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle external action intent.

        Args:
            user_input: User input text
            entities: Extracted entities
            metadata: Intent metadata

        Returns:
            Handler result
        """
        logger.info(f"Handling external action: {user_input}")

        lookup_query = entities.get("lookup_query", "")

        if not lookup_query:
            return {
                "action": "llm_response",
                "message": "I'm not sure what you want me to look up.",
                "debug": self._get_debug_info(user_input, entities, metadata) if self.debug_mode else None
            }

        # If we have a tool router, try to use a search tool
        if self.tool_router:
            try:
                # Check if we have a web search tool
                if hasattr(self.tool_router, 'has_tool') and self.tool_router.has_tool('web_search'):
                    return {
                        "action": "tool_call",
                        "tool": "web_search",
                        "args": {"query": lookup_query},
                        "message": f"Searching for information about '{lookup_query}'",
                        "debug": self._get_debug_info(user_input, entities, metadata) if self.debug_mode else None
                    }
            except Exception as e:
                logger.error(f"Error calling search tool: {e}")
                return {
                    "action": "error",
                    "message": f"I encountered an error while trying to search for '{lookup_query}'",
                    "error": str(e),
                    "debug": self._get_debug_info(user_input, entities, metadata) if self.debug_mode else None
                }

        # If no tool router or search tool, let the LLM handle it
        return {
            "action": "llm_response",
            "message": f"I would search for information about '{lookup_query}' if I could.",
            "debug": self._get_debug_info(user_input, entities, metadata) if self.debug_mode else None
        }

    def handle_tool_use(self, user_input: str, entities: Dict[str, Any], metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle tool use intent.

        Args:
            user_input: User input text
            entities: Extracted entities
            metadata: Intent metadata

        Returns:
            Handler result
        """
        logger.info(f"Handling tool use: {user_input}")

        # For tool use, we'll let the LLM and tool router handle it
        return {
            "action": "llm_response",
            "message": "Processing tool use request",
            "debug": self._get_debug_info(user_input, entities, metadata) if self.debug_mode else None
        }

    def handle_future_planning(self, user_input: str, entities: Dict[str, Any], metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle future planning intent.

        Args:
            user_input: User input text
            entities: Extracted entities
            metadata: Intent metadata

        Returns:
            Handler result
        """
        logger.info(f"Handling future planning: {user_input}")

        reminder_content = entities.get("reminder_content", "")
        reminder_time = entities.get("reminder_time", "")

        if not reminder_content:
            return {
                "action": "llm_response",
                "message": "I'm not sure what you want me to remind you about.",
                "debug": self._get_debug_info(user_input, entities, metadata) if self.debug_mode else None
            }

        # For now, just acknowledge the reminder (future implementation)
        return {
            "action": "future_planning",
            "reminder_content": reminder_content,
            "reminder_time": reminder_time,
            "message": f"I would remind you to {reminder_content} {reminder_time if reminder_time else 'later'} if I could.",
            "debug": self._get_debug_info(user_input, entities, metadata) if self.debug_mode else None
        }

    def handle_user_preference(self, user_input: str, entities: Dict[str, Any], metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle user preference intent.

        Args:
            user_input: User input text
            entities: Extracted entities
            metadata: Intent metadata

        Returns:
            Handler result
        """
        logger.info(f"Handling user preference: {user_input}")

        # If we have a memory manager, store the preference
        if self.memory_manager and hasattr(self.memory_manager, 'add_preference'):
            try:
                # For now, just store the whole input as a preference
                preference_id = self.memory_manager.add_preference(user_input)

                return {
                    "action": "preference_store",
                    "preference": user_input,
                    "preference_id": preference_id,
                    "message": "I've noted your preference.",
                    "debug": self._get_debug_info(user_input, entities, metadata) if self.debug_mode else None
                }
            except Exception as e:
                logger.error(f"Error storing preference: {e}")

        # If no memory manager or error, let the LLM handle it
        return {
            "action": "llm_response",
            "message": "Processing preference",
            "debug": self._get_debug_info(user_input, entities, metadata) if self.debug_mode else None
        }

    def handle_conversation_control(self, user_input: str, entities: Dict[str, Any], metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle conversation control intent.

        Args:
            user_input: User input text
            entities: Extracted entities
            metadata: Intent metadata

        Returns:
            Handler result
        """
        logger.info(f"Handling conversation control: {user_input}")

        # For conversation control, we'll let the LLM handle it
        return {
            "action": "llm_response",
            "message": "Processing conversation control",
            "debug": self._get_debug_info(user_input, entities, metadata) if self.debug_mode else None
        }

    def handle_personality_adjustment(self, user_input: str, entities: Dict[str, Any], metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle personality adjustment intent.

        Args:
            user_input: User input text
            entities: Extracted entities
            metadata: Intent metadata

        Returns:
            Handler result
        """
        logger.info(f"Handling personality adjustment: {user_input}")

        trait = entities.get("adjustment_trait", "")
        direction = entities.get("adjustment_direction", "")

        if not trait or not direction:
            return {
                "action": "llm_response",
                "message": "I'm not sure how you want me to adjust my personality.",
                "debug": self._get_debug_info(user_input, entities, metadata) if self.debug_mode else None
            }

        # If we have a personality manager, adjust the personality
        if self.personality_manager and hasattr(self.personality_manager, 'parameters'):
            try:
                # Map common traits to personality parameters
                trait_map = {
                    "verbose": "verbosity",
                    "talkative": "verbosity",
                    "detailed": "verbosity",
                    "concise": "verbosity",
                    "brief": "verbosity",
                    "assertive": "assertiveness",
                    "confident": "assertiveness",
                    "tentative": "assertiveness",
                    "funny": "humor",
                    "humorous": "humor",
                    "serious": "humor",
                    "formal": "formality",
                    "professional": "formality",
                    "casual": "formality",
                    "relaxed": "formality",
                    "proactive": "proactivity",
                    "reactive": "proactivity",
                    "helpful": "proactivity"
                }

                # Find the closest trait
                param_name = None
                for key, value in trait_map.items():
                    if key in trait.lower():
                        param_name = value
                        break

                if param_name:
                    # Get current value
                    current_value = self.personality_manager.parameters.get_parameter_value(param_name)

                    # Adjust value
                    adjustment = 0.2 if direction == "more" else -0.2

                    # Handle special cases
                    if param_name == "humor" and "serious" in trait.lower():
                        adjustment = -0.2  # Being more serious means less humor
                    elif param_name == "verbosity" and ("concise" in trait.lower() or "brief" in trait.lower()):
                        adjustment = -0.2  # Being more concise means less verbosity

                    # Set new value
                    self.personality_manager.parameters.set_parameter_value(
                        param_name,
                        current_value + adjustment,
                        reason=f"user_request:{trait}"
                    )

                    return {
                        "action": "personality_adjustment",
                        "parameter": param_name,
                        "adjustment": adjustment,
                        "new_value": current_value + adjustment,
                        "message": f"I'll try to be {'more' if adjustment > 0 else 'less'} {trait}.",
                        "debug": self._get_debug_info(user_input, entities, metadata) if self.debug_mode else None
                    }
            except Exception as e:
                logger.error(f"Error adjusting personality: {e}")

        # If no personality manager or error, let the LLM handle it
        return {
            "action": "llm_response",
            "message": f"I'll try to be {direction} {trait}.",
            "debug": self._get_debug_info(user_input, entities, metadata) if self.debug_mode else None
        }

    def handle_system_command(self, user_input: str, entities: Dict[str, Any], metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle system command intent.

        Args:
            user_input: User input text
            entities: Extracted entities
            metadata: Intent metadata

        Returns:
            Handler result
        """
        logger.info(f"Handling system command: {user_input}")

        command = entities.get("command", "")
        args = entities.get("args", [])

        if not command:
            return {
                "action": "error",
                "message": "Invalid system command",
                "debug": self._get_debug_info(user_input, entities, metadata) if self.debug_mode else None
            }

        # Handle different commands
        if command == "reset_tone":
            if args and len(args) > 0:
                tone = args[0]

                # If we have a personality manager, reset the tone
                if self.personality_manager and hasattr(self.personality_manager, 'reset'):
                    try:
                        self.personality_manager.reset()

                        # Apply the specified tone
                        if tone == "casual":
                            self.personality_manager.parameters.set_parameter_value("formality", 0.3, reason="user_command:reset_tone")
                            self.personality_manager.parameters.set_parameter_value("humor", 0.6, reason="user_command:reset_tone")
                        elif tone == "formal":
                            self.personality_manager.parameters.set_parameter_value("formality", 0.8, reason="user_command:reset_tone")
                            self.personality_manager.parameters.set_parameter_value("humor", 0.2, reason="user_command:reset_tone")
                        elif tone == "technical":
                            self.personality_manager.parameters.set_parameter_value("verbosity", 0.7, reason="user_command:reset_tone")
                            self.personality_manager.parameters.set_parameter_value("formality", 0.7, reason="user_command:reset_tone")
                        elif tone == "concise":
                            self.personality_manager.parameters.set_parameter_value("verbosity", 0.2, reason="user_command:reset_tone")

                        return {
                            "action": "system_command",
                            "command": command,
                            "args": args,
                            "message": f"Tone reset to {tone}",
                            "debug": self._get_debug_info(user_input, entities, metadata) if self.debug_mode else None
                        }
                    except Exception as e:
                        logger.error(f"Error resetting tone: {e}")
                        return {
                            "action": "error",
                            "message": f"Error resetting tone: {e}",
                            "debug": self._get_debug_info(user_input, entities, metadata) if self.debug_mode else None
                        }

            return {
                "action": "system_command",
                "command": command,
                "args": args,
                "message": "Please specify a tone (casual, formal, technical, concise)",
                "debug": self._get_debug_info(user_input, entities, metadata) if self.debug_mode else None
            }

        elif command == "show_memory":
            # If we have a memory manager, show memory stats
            if self.memory_manager and hasattr(self.memory_manager, 'get_memory_stats'):
                try:
                    stats = self.memory_manager.get_memory_stats()

                    return {
                        "action": "system_command",
                        "command": command,
                        "args": args,
                        "stats": stats,
                        "message": "Memory statistics retrieved",
                        "debug": self._get_debug_info(user_input, entities, metadata) if self.debug_mode else None
                    }
                except Exception as e:
                    logger.error(f"Error getting memory stats: {e}")
                    return {
                        "action": "error",
                        "message": f"Error getting memory stats: {e}",
                        "debug": self._get_debug_info(user_input, entities, metadata) if self.debug_mode else None
                    }

            return {
                "action": "system_command",
                "command": command,
                "args": args,
                "message": "Memory manager not available",
                "debug": self._get_debug_info(user_input, entities, metadata) if self.debug_mode else None
            }

        elif command == "summarize_session":
            # If we have a session manager, generate a summary
            if self.personality_manager and hasattr(self.personality_manager, 'session_manager'):
                try:
                    summary = self.personality_manager.session_manager.generate_session_summary()

                    return {
                        "action": "system_command",
                        "command": command,
                        "args": args,
                        "summary": summary,
                        "message": "Session summary generated",
                        "debug": self._get_debug_info(user_input, entities, metadata) if self.debug_mode else None
                    }
                except Exception as e:
                    logger.error(f"Error generating session summary: {e}")
                    return {
                        "action": "error",
                        "message": f"Error generating session summary: {e}",
                        "debug": self._get_debug_info(user_input, entities, metadata) if self.debug_mode else None
                    }

            return {
                "action": "system_command",
                "command": command,
                "args": args,
                "message": "Session manager not available",
                "debug": self._get_debug_info(user_input, entities, metadata) if self.debug_mode else None
            }

        elif command == "debug_on":
            self.debug_mode = True
            return {
                "action": "system_command",
                "command": command,
                "args": args,
                "message": "Debug mode enabled",
                "debug": self._get_debug_info(user_input, entities, metadata)
            }

        elif command == "debug_off":
            self.debug_mode = False
            return {
                "action": "system_command",
                "command": command,
                "args": args,
                "message": "Debug mode disabled",
                "debug": None
            }

        elif command == "mood_reset":
            # Reset personality to default mood
            if self.personality_manager and hasattr(self.personality_manager, 'reset'):
                try:
                    self.personality_manager.reset()

                    return {
                        "action": "system_command",
                        "command": command,
                        "args": args,
                        "message": "Mood reset to default state. I'm feeling balanced and ready to help.",
                        "debug": self._get_debug_info(user_input, entities, metadata) if self.debug_mode else None
                    }
                except Exception as e:
                    logger.error(f"Error resetting mood: {e}")
                    return {
                        "action": "error",
                        "message": f"Error resetting mood: {e}",
                        "debug": self._get_debug_info(user_input, entities, metadata) if self.debug_mode else None
                    }

            return {
                "action": "system_command",
                "command": command,
                "args": args,
                "message": "Personality manager not available",
                "debug": self._get_debug_info(user_input, entities, metadata) if self.debug_mode else None
            }

        elif command == "apply_feedback":
            # Apply feedback patterns to personality
            if self.personality_manager and hasattr(self.personality_manager, 'apply_feedback_patterns'):
                try:
                    # Apply feedback patterns
                    result = self.personality_manager.apply_feedback_patterns()

                    if result.get("applied", False):
                        changes = result.get("changes", [])

                        # Format changes for display
                        changes_text = ""
                        if changes:
                            changes_text = "\n\nApplied changes:\n"
                            for change in changes:
                                param = change.get("parameter", "unknown")
                                old_val = change.get("old_value", 0)
                                new_val = change.get("new_value", 0)
                                reason = change.get("reason", "unknown")
                                changes_text += f"- {param}: {old_val:.2f} → {new_val:.2f} ({reason})\n"

                        return {
                            "action": "system_command",
                            "command": command,
                            "args": args,
                            "result": result,
                            "message": f"Successfully applied feedback patterns to personality.{changes_text}",
                            "debug": self._get_debug_info(user_input, entities, metadata) if self.debug_mode else None
                        }
                    else:
                        reason = result.get("reason", "unknown")
                        return {
                            "action": "system_command",
                            "command": command,
                            "args": args,
                            "result": result,
                            "message": f"No changes applied from feedback patterns: {reason}",
                            "debug": self._get_debug_info(user_input, entities, metadata) if self.debug_mode else None
                        }
                except Exception as e:
                    logger.error(f"Error applying feedback patterns: {e}")
                    return {
                        "action": "error",
                        "message": f"Error applying feedback patterns: {e}",
                        "debug": self._get_debug_info(user_input, entities, metadata) if self.debug_mode else None
                    }

            return {
                "action": "system_command",
                "command": command,
                "args": args,
                "message": "Personality manager not available or doesn't support feedback pattern application",
                "debug": self._get_debug_info(user_input, entities, metadata) if self.debug_mode else None
            }

        elif command == "personality_insight":
            # Provide insight into current personality settings
            if self.personality_manager and hasattr(self.personality_manager, 'parameters'):
                try:
                    # Get current parameter values
                    parameters = {}
                    for param_name in ["verbosity", "formality", "humor", "assertiveness", "proactivity"]:
                        if hasattr(self.personality_manager.parameters, 'get_parameter_value'):
                            parameters[param_name] = self.personality_manager.parameters.get_parameter_value(param_name)

                    # Generate a human-readable description
                    descriptions = []
                    if "verbosity" in parameters:
                        if parameters["verbosity"] > 0.7:
                            descriptions.append("I'm currently being quite detailed in my responses.")
                        elif parameters["verbosity"] < 0.3:
                            descriptions.append("I'm trying to be concise and to the point.")
                        else:
                            descriptions.append("I'm balancing detail and brevity in my responses.")

                    if "formality" in parameters:
                        if parameters["formality"] > 0.7:
                            descriptions.append("My tone is quite formal and professional.")
                        elif parameters["formality"] < 0.3:
                            descriptions.append("I'm using a casual, conversational tone.")
                        else:
                            descriptions.append("I'm using a moderately formal tone.")

                    if "humor" in parameters:
                        if parameters["humor"] > 0.7:
                            descriptions.append("I'm trying to be light-hearted and inject some humor.")
                        elif parameters["humor"] < 0.3:
                            descriptions.append("I'm keeping things serious and straightforward.")
                        else:
                            descriptions.append("I'm using a balanced approach to humor.")

                    if "assertiveness" in parameters:
                        if parameters["assertiveness"] > 0.7:
                            descriptions.append("I'm being quite confident and direct in my responses.")
                        elif parameters["assertiveness"] < 0.3:
                            descriptions.append("I'm being tentative and careful with my statements.")
                        else:
                            descriptions.append("I'm balancing confidence with caution.")

                    if "proactivity" in parameters:
                        if parameters["proactivity"] > 0.7:
                            descriptions.append("I'm being proactive and offering additional information.")
                        elif parameters["proactivity"] < 0.3:
                            descriptions.append("I'm being reactive and focusing on direct responses.")
                        else:
                            descriptions.append("I'm balancing reactive and proactive approaches.")

                    # Get behavioral state if available
                    behavioral_state = ""
                    if hasattr(self.personality_manager, 'behavioral_conditioner') and \
                       hasattr(self.personality_manager.behavioral_conditioner, 'get_current_state'):
                        try:
                            state = self.personality_manager.behavioral_conditioner.get_current_state()
                            if state:
                                behavioral_state = f"\n\nBehavioral state: {state}"
                        except:
                            pass

                    # Get user preference insights if available
                    preference_insights = ""
                    if hasattr(self.personality_manager, 'get_user_preference_insights'):
                        try:
                            insights = self.personality_manager.get_user_preference_insights()
                            if insights.get("available", False):
                                preference_insights = "\n\nLearned preferences:\n"
                                for param, prefs in insights.get("preferences", {}).items():
                                    for pref in prefs:
                                        preference = pref.get("preference", "unknown")
                                        confidence = pref.get("confidence", 0)
                                        source = pref.get("source", "unknown")
                                        preference_insights += f"- {param}: {preference} (confidence: {confidence:.2f}, source: {source})\n"
                        except Exception as e:
                            logger.error(f"Error getting user preference insights: {e}")

                    # Combine descriptions
                    message = "Current personality settings:\n\n" + "\n".join(descriptions) + behavioral_state + preference_insights

                    return {
                        "action": "system_command",
                        "command": command,
                        "args": args,
                        "parameters": parameters,
                        "message": message,
                        "debug": self._get_debug_info(user_input, entities, metadata) if self.debug_mode else None
                    }
                except Exception as e:
                    logger.error(f"Error getting personality insight: {e}")
                    return {
                        "action": "error",
                        "message": f"Error getting personality insight: {e}",
                        "debug": self._get_debug_info(user_input, entities, metadata) if self.debug_mode else None
                    }

            return {
                "action": "system_command",
                "command": command,
                "args": args,
                "message": "Personality manager not available",
                "debug": self._get_debug_info(user_input, entities, metadata) if self.debug_mode else None
            }

        elif command == "summarize_day":
            # Generate a summary of the day's interactions
            if self.memory_manager and hasattr(self.memory_manager, 'get_day_summary'):
                try:
                    summary = self.memory_manager.get_day_summary()

                    if summary:
                        return {
                            "action": "system_command",
                            "command": command,
                            "args": args,
                            "summary": summary,
                            "message": f"Here's a summary of our interactions today:\n\n{summary}",
                            "debug": self._get_debug_info(user_input, entities, metadata) if self.debug_mode else None
                        }
                    else:
                        return {
                            "action": "system_command",
                            "command": command,
                            "args": args,
                            "message": "I don't have enough information to generate a day summary yet.",
                            "debug": self._get_debug_info(user_input, entities, metadata) if self.debug_mode else None
                        }
                except Exception as e:
                    logger.error(f"Error generating day summary: {e}")
                    return {
                        "action": "error",
                        "message": f"Error generating day summary: {e}",
                        "debug": self._get_debug_info(user_input, entities, metadata) if self.debug_mode else None
                    }

            return {
                "action": "system_command",
                "command": command,
                "args": args,
                "message": "Memory manager not available or doesn't support day summaries",
                "debug": self._get_debug_info(user_input, entities, metadata) if self.debug_mode else None
            }

        elif command == "view_feedback_memories":
            # View feedback memories from long-term memory
            feedback_type = args[0] if args and len(args) > 0 else None

            if self.memory_manager and hasattr(self.memory_manager, 'get_feedback_memories'):
                try:
                    # Get feedback memories
                    memories = self.memory_manager.get_feedback_memories(feedback_type=feedback_type, limit=10)

                    if memories:
                        # Format the memories
                        memory_text = "\n\n".join([
                            f"- {memory.get('content', '')}\n  Sentiment: {memory.get('sentiment', 'unknown')}\n  Type: {memory.get('type', 'unknown')}\n  Time: {memory.get('timestamp', 'unknown')}"
                            for memory in memories
                        ])

                        message = f"Feedback memories{' of type ' + feedback_type if feedback_type else ''} ({len(memories)} items):\n\n{memory_text}"
                    else:
                        message = f"No feedback memories{' of type ' + feedback_type if feedback_type else ''} found."

                    return {
                        "action": "system_command",
                        "command": command,
                        "args": args,
                        "memories": memories,
                        "message": message,
                        "debug": self._get_debug_info(user_input, entities, metadata) if self.debug_mode else None
                    }
                except Exception as e:
                    logger.error(f"Error getting feedback memories: {e}")
                    return {
                        "action": "error",
                        "message": f"Error getting feedback memories: {e}",
                        "debug": self._get_debug_info(user_input, entities, metadata) if self.debug_mode else None
                    }

            return {
                "action": "system_command",
                "command": command,
                "args": args,
                "message": "Memory manager not available or doesn't support feedback memories",
                "debug": self._get_debug_info(user_input, entities, metadata) if self.debug_mode else None
            }

        elif command == "view_feedback":
            # View feedback history or specific feedback type
            feedback_type = args[0] if args and len(args) > 0 else None

            # Check if we have a feedback manager available through the personality manager
            feedback_manager = None
            if self.personality_manager and hasattr(self.personality_manager, 'feedback_manager'):
                feedback_manager = self.personality_manager.feedback_manager

            if feedback_manager and hasattr(feedback_manager, 'get_feedback_stats'):
                try:
                    stats = feedback_manager.get_feedback_stats()

                    if feedback_type:
                        # Filter by specific feedback type
                        filtered_history = []
                        for item in feedback_manager.get_feedback_history():
                            item_type = item["type"].name if hasattr(item["type"], "name") else str(item["type"])
                            if item_type.lower() == feedback_type.lower():
                                filtered_history.append(item)

                        if filtered_history:
                            # Format the feedback items
                            feedback_text = "\n".join([
                                f"- {item['prompt']} Response: '{item['response']}' (Sentiment: {item['sentiment']})"
                                for item in filtered_history
                            ])

                            message = f"Feedback of type '{feedback_type}' ({len(filtered_history)} items):\n\n{feedback_text}"
                        else:
                            message = f"No feedback of type '{feedback_type}' found."
                    else:
                        # Show overall statistics
                        message = f"Feedback statistics:\n\n"
                        message += f"Total feedback: {stats['total']}\n"
                        message += f"Positive: {stats['positive']}\n"
                        message += f"Negative: {stats['negative']}\n"
                        message += f"Neutral: {stats['neutral']}\n\n"

                        if stats['by_type']:
                            message += "Feedback by type:\n"
                            for type_name, count in stats['by_type'].items():
                                message += f"- {type_name}: {count}\n"

                    return {
                        "action": "system_command",
                        "command": command,
                        "args": args,
                        "stats": stats,
                        "message": message,
                        "debug": self._get_debug_info(user_input, entities, metadata) if self.debug_mode else None
                    }
                except Exception as e:
                    logger.error(f"Error getting feedback stats: {e}")
                    return {
                        "action": "error",
                        "message": f"Error getting feedback stats: {e}",
                        "debug": self._get_debug_info(user_input, entities, metadata) if self.debug_mode else None
                    }

            return {
                "action": "system_command",
                "command": command,
                "args": args,
                "message": "Feedback manager not available",
                "debug": self._get_debug_info(user_input, entities, metadata) if self.debug_mode else None
            }

        elif command == "feedback":
            # Manually provide feedback of a specific type
            feedback_type = args[0] if args and len(args) > 0 else "general"

            # Check if we have a feedback manager available through the personality manager
            feedback_manager = None
            if self.personality_manager and hasattr(self.personality_manager, 'feedback_manager'):
                feedback_manager = self.personality_manager.feedback_manager

            if feedback_manager:
                try:
                    # Create a feedback request for the specified type
                    valid_types = ["helpfulness", "memory", "tone", "verbosity", "accuracy", "general"]

                    if feedback_type.lower() not in valid_types:
                        return {
                            "action": "system_command",
                            "command": command,
                            "args": args,
                            "message": f"Invalid feedback type. Valid types are: {', '.join(valid_types)}",
                            "debug": self._get_debug_info(user_input, entities, metadata) if self.debug_mode else None
                        }

                    # Map the string to the enum
                    from feedback import FeedbackType
                    feedback_enum = getattr(FeedbackType, feedback_type.upper())

                    # Get a prompt for this feedback type
                    from feedback import FeedbackPrompt
                    prompt_options = getattr(FeedbackPrompt, feedback_type.upper()).value
                    prompt_text = random.choice(prompt_options)

                    # Create a mock intent result for the feedback request
                    mock_intent_result = {
                        "intent_type": "MANUAL_FEEDBACK",
                        "action": "feedback_request",
                        "message": "Manual feedback request"
                    }

                    # Create the feedback request
                    feedback_request = {
                        "id": f"feedback_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                        "type": feedback_enum,
                        "prompt": prompt_text,
                        "intent_type": "MANUAL_FEEDBACK",
                        "intent_result": mock_intent_result,
                        "timestamp": datetime.now().isoformat(),
                        "turn": feedback_manager.current_turn
                    }

                    # Set as active feedback request
                    feedback_manager.active_feedback_request = feedback_request

                    return {
                        "action": "system_command",
                        "command": command,
                        "args": args,
                        "feedback_type": feedback_type,
                        "prompt": prompt_text,
                        "message": prompt_text,
                        "debug": self._get_debug_info(user_input, entities, metadata) if self.debug_mode else None
                    }
                except Exception as e:
                    logger.error(f"Error creating feedback request: {e}")
                    return {
                        "action": "error",
                        "message": f"Error creating feedback request: {e}",
                        "debug": self._get_debug_info(user_input, entities, metadata) if self.debug_mode else None
                    }

            return {
                "action": "system_command",
                "command": command,
                "args": args,
                "message": "Feedback manager not available",
                "debug": self._get_debug_info(user_input, entities, metadata) if self.debug_mode else None
            }

        elif command == "help":
            # Show available commands
            commands = [
                # Personality commands
                "#reset_tone [casual|formal|technical|concise] - Reset personality tone",
                "#mood_reset - Reset personality to default state",
                "#personality_insight - Show current personality settings",
                "#apply_feedback - Apply feedback patterns to personality",

                # Memory commands
                "#show_memory - Show memory statistics",
                "#summarize_session - Generate a summary of the current session",
                "#summarize_day - Generate a summary of today's interactions",
                "#view_feedback [type] - View feedback history or specific type",
                "#view_feedback_memories [type] - View feedback memories from long-term memory",

                # Feedback commands
                "#feedback [type] - Request specific feedback (helpfulness, memory, tone, verbosity, accuracy, general)",

                # System commands
                "#debug_on - Enable debug mode",
                "#debug_off - Disable debug mode",
                "#help - Show this help message"
            ]

            return {
                "action": "system_command",
                "command": command,
                "args": args,
                "commands": commands,
                "message": "Available commands:\n" + "\n".join(commands),
                "debug": self._get_debug_info(user_input, entities, metadata) if self.debug_mode else None
            }

        # Unknown command
        return {
            "action": "error",
            "message": f"Unknown command: {command}",
            "debug": self._get_debug_info(user_input, entities, metadata) if self.debug_mode else None
        }

    def handle_greeting(self, user_input: str, entities: Dict[str, Any], metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle greeting intent.

        Args:
            user_input: User input text
            entities: Extracted entities
            metadata: Intent metadata

        Returns:
            Handler result
        """
        logger.info(f"Handling greeting: {user_input}")

        # For greetings, we'll let the LLM handle it
        return {
            "action": "llm_response",
            "message": "Processing greeting",
            "debug": self._get_debug_info(user_input, entities, metadata) if self.debug_mode else None
        }

    def handle_farewell(self, user_input: str, entities: Dict[str, Any], metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle farewell intent.

        Args:
            user_input: User input text
            entities: Extracted entities
            metadata: Intent metadata

        Returns:
            Handler result
        """
        logger.info(f"Handling farewell: {user_input}")

        # For farewells, we'll let the LLM handle it
        return {
            "action": "llm_response",
            "message": "Processing farewell",
            "debug": self._get_debug_info(user_input, entities, metadata) if self.debug_mode else None
        }

    def handle_gratitude(self, user_input: str, entities: Dict[str, Any], metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle gratitude intent.

        Args:
            user_input: User input text
            entities: Extracted entities
            metadata: Intent metadata

        Returns:
            Handler result
        """
        logger.info(f"Handling gratitude: {user_input}")

        # For gratitude, we'll let the LLM handle it
        return {
            "action": "llm_response",
            "message": "Processing gratitude",
            "debug": self._get_debug_info(user_input, entities, metadata) if self.debug_mode else None
        }

    def handle_feedback(self, user_input: str, entities: Dict[str, Any], metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle feedback intent.

        Args:
            user_input: User input text
            entities: Extracted entities
            metadata: Intent metadata

        Returns:
            Handler result
        """
        logger.info(f"Handling feedback: {user_input}")

        # For feedback, we'll let the LLM handle it
        return {
            "action": "llm_response",
            "message": "Processing feedback",
            "debug": self._get_debug_info(user_input, entities, metadata) if self.debug_mode else None
        }

    def handle_unknown(self, user_input: str, entities: Dict[str, Any], metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle unknown intent.

        Args:
            user_input: User input text
            entities: Extracted entities
            metadata: Intent metadata

        Returns:
            Handler result
        """
        logger.info(f"Handling unknown intent: {user_input}")

        # For unknown intents, we'll let the LLM handle it
        return {
            "action": "llm_response",
            "message": "Processing request",
            "debug": self._get_debug_info(user_input, entities, metadata) if self.debug_mode else None
        }

    def _get_debug_info(self, user_input: str, entities: Dict[str, Any], metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get debug information.

        Args:
            user_input: User input text
            entities: Extracted entities
            metadata: Intent metadata

        Returns:
            Debug information
        """
        return {
            "user_input": user_input,
            "entities": entities,
            "metadata": metadata
        }

    def get_all_handlers(self) -> Dict[IntentType, callable]:
        """
        Get all intent handlers.

        Returns:
            Dictionary mapping intent types to handler functions
        """
        return {
            IntentType.INFORMATION_REQUEST: self.handle_information_request,
            IntentType.MEMORY_RECALL: self.handle_memory_recall,
            IntentType.MEMORY_STORE: self.handle_memory_store,
            IntentType.EXTERNAL_ACTION: self.handle_external_action,
            IntentType.TOOL_USE: self.handle_tool_use,
            IntentType.FUTURE_PLANNING: self.handle_future_planning,
            IntentType.USER_PREFERENCE: self.handle_user_preference,
            IntentType.CONVERSATION_CONTROL: self.handle_conversation_control,
            IntentType.PERSONALITY_ADJUSTMENT: self.handle_personality_adjustment,
            IntentType.SYSTEM_COMMAND: self.handle_system_command,
            IntentType.GREETING: self.handle_greeting,
            IntentType.FAREWELL: self.handle_farewell,
            IntentType.GRATITUDE: self.handle_gratitude,
            IntentType.FEEDBACK: self.handle_feedback,
            IntentType.UNKNOWN: self.handle_unknown
        }
