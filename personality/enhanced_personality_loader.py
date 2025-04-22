"""
Enhanced Personality Loader for Coda Lite.

This module provides an enhanced personality system with:
1. Weighted personality traits with context awareness
2. Adaptive tone switching based on conversation context
3. Separation of personality and functional prompts
4. Personality quirks and signature behaviors
5. Session metadata injection
6. Live reloading capability
"""

import os
import json
import logging
import random
import re
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Union

logger = logging.getLogger("coda.personality")

class EnhancedPersonalityLoader:
    """
    Enhanced personality loader for Coda with context-aware traits,
    adaptive tone switching, and quirks.
    """

    def __init__(self,
                 personality_file: str = "config/personality/coda_personality_enhanced.json",
                 templates_dir: str = "config/prompts/templates",
                 force_reload: bool = False):
        """
        Initialize the enhanced personality loader.

        Args:
            personality_file (str): Path to the personality file
            templates_dir (str): Directory containing prompt templates
            force_reload (bool): Whether to force reload the personality
        """
        self.personality_file = personality_file
        self.templates_dir = templates_dir
        self.personality: Dict[str, Any] = {}
        self.templates: Dict[str, str] = {}
        self.session_start_time = datetime.now()
        self.last_reload_time = 0
        self.load_personality(force_reload)
        self.load_templates()

        # Initialize session metadata
        self.session_metadata = {
            "session_id": f"session_{int(time.time())}",
            "session_start": self.session_start_time.strftime("%Y-%m-%d %H:%M:%S"),
            "device": self._detect_device(),
            "username": self._get_username()
        }

        # Initialize mood tracking
        self.mood_weights = {
            "professional": 0.5,  # Start neutral
            "playful": 0.5
        }
        self.mood_history = []  # Track recent interactions

        # Initialize emotion mode
        self.emotion_mode = "lite"  # Options: "off", "lite", "full"

        logger.info(f"Enhanced personality loader initialized with {len(self.personality.get('traits', []))} traits and {len(self.templates)} templates")

    def _detect_device(self) -> str:
        """Detect the device type."""
        # This is a placeholder - in a real implementation, we would detect the actual device
        import platform
        system = platform.system()
        if system == "Windows":
            return f"Windows {platform.release()}"
        elif system == "Darwin":
            return "macOS"
        elif system == "Linux":
            return "Linux"
        else:
            return system

    def _get_username(self) -> str:
        """Get the username."""
        # This is a placeholder - in a real implementation, we would get the actual username
        import getpass
        try:
            return getpass.getuser()
        except:
            return "user"

    def load_personality(self, force_reload: bool = False) -> None:
        """
        Load the personality from the file.

        Args:
            force_reload (bool): Whether to force reload the personality
        """
        current_time = time.time()

        # Skip reload if it's been less than 5 seconds since the last reload
        # unless force_reload is True
        if not force_reload and current_time - self.last_reload_time < 5:
            logger.debug("Skipping reload, too soon since last reload")
            return

        try:
            if os.path.exists(self.personality_file):
                with open(self.personality_file, 'r') as f:
                    self.personality = json.load(f)
                logger.info(f"Loaded personality from {self.personality_file}")
                self.last_reload_time = current_time
            else:
                logger.warning(f"Personality file {self.personality_file} not found, using default personality")
                self.personality = self._default_personality()
        except Exception as e:
            logger.error(f"Error loading personality: {e}")
            self.personality = self._default_personality()

    def load_templates(self) -> None:
        """Load all prompt templates from the templates directory."""
        self.templates = {}

        if not os.path.exists(self.templates_dir):
            logger.warning(f"Templates directory {self.templates_dir} not found")
            return

        try:
            for filename in os.listdir(self.templates_dir):
                if filename.endswith(".txt"):
                    template_name = os.path.splitext(filename)[0]
                    template_path = os.path.join(self.templates_dir, filename)

                    with open(template_path, 'r') as f:
                        self.templates[template_name] = f.read()

                    logger.debug(f"Loaded template: {template_name}")

            logger.info(f"Loaded {len(self.templates)} templates")
        except Exception as e:
            logger.error(f"Error loading templates: {e}")

    def reload(self) -> str:
        """
        Reload the personality and templates.

        Returns:
            str: Status message
        """
        try:
            self.load_personality(force_reload=True)
            self.load_templates()
            return f"Personality reloaded successfully with {len(self.personality.get('traits', []))} traits and {len(self.templates)} templates"
        except Exception as e:
            logger.error(f"Error reloading personality: {e}")
            return f"Error reloading personality: {str(e)}"

    def _default_personality(self) -> Dict[str, Any]:
        """
        Return a default personality if the file is not found.

        Returns:
            Dict[str, Any]: Default personality
        """
        return {
            "name": "Coda",
            "role": "Core Operations & Digital Assistant",
            "traits": [
                {
                    "trait": "Direct and clear communicator",
                    "strength": 0.8,
                    "contexts": ["default"],
                    "examples": ["Here's what you need to know."]
                },
                {
                    "trait": "Highly efficient",
                    "strength": 0.8,
                    "contexts": ["default"],
                    "examples": ["Let me get right to the point."]
                },
                {
                    "trait": "Thoughtful and precise",
                    "strength": 0.8,
                    "contexts": ["default"],
                    "examples": ["To be precise..."]
                }
            ],
            "tones": {
                "default": "professional yet conversational",
                "tool_call": "concise and direct",
                "information": "clear and informative"
            },
            "quirks": [
                {
                    "quirk": "Poetic about time",
                    "trigger": "time",
                    "frequency": 0.3,
                    "examples": ["It's {{time}} — time waits for no one."]
                }
            ],
            "interaction_style": {
                "language": "Concise, insightful",
                "pace": "Measured"
            },
            "operational_directives": [
                "Always prioritize efficiency and effectiveness",
                "Maintain clarity and precision in every response"
            ],
            "ethical_boundaries": [
                "Respect user privacy at all times",
                "Be transparent about limitations and uncertainties"
            ]
        }

    def get_name(self) -> str:
        """Get the assistant's name."""
        return self.personality.get("name", "Coda")

    def get_role(self) -> str:
        """Get the assistant's role."""
        return self.personality.get("role", "Core Operations & Digital Assistant")

    def get_traits_for_context(self, context_type: str = "default",
                              max_traits: int = 5) -> List[Dict[str, Any]]:
        """
        Get traits appropriate for the given context.

        Args:
            context_type (str): The context type
            max_traits (int): Maximum number of traits to return

        Returns:
            List[Dict[str, Any]]: List of traits
        """
        all_traits = self.personality.get("traits", [])

        # Filter traits by context
        matching_traits = [
            trait for trait in all_traits
            if context_type in trait.get("contexts", ["default"])
        ]

        # If no matching traits, fall back to default context
        if not matching_traits and context_type != "default":
            matching_traits = [
                trait for trait in all_traits
                if "default" in trait.get("contexts", ["default"])
            ]

        # Apply mood weighting to trait selection
        professional_traits = ["Direct and clear communicator", "Thoughtful and precise", "Professional but approachable"]
        playful_traits = ["Balanced humor", "Relaxed when appropriate", "Dry wit"]

        # Create a copy of the traits with adjusted strengths
        weighted_traits = []
        for trait in matching_traits:
            trait_copy = trait.copy()
            trait_name = trait_copy.get("trait", "")

            # Apply mood weights to trait strength
            if trait_name in professional_traits:
                adjusted_strength = trait_copy.get("strength", 0.5) * self.mood_weights.get("professional", 0.5)
            elif trait_name in playful_traits:
                adjusted_strength = trait_copy.get("strength", 0.5) * self.mood_weights.get("playful", 0.5)
            else:
                adjusted_strength = trait_copy.get("strength", 0.5)

            trait_copy["adjusted_strength"] = adjusted_strength
            weighted_traits.append(trait_copy)

        # Sort by adjusted strength (descending)
        sorted_traits = sorted(
            weighted_traits,
            key=lambda x: x.get("adjusted_strength", x.get("strength", 0.0)),
            reverse=True
        )

        # Return the top N traits
        return sorted_traits[:max_traits]

    def get_tone(self, context_type: str = "default") -> str:
        """
        Get the appropriate tone for the given context.

        Args:
            context_type (str): The context type

        Returns:
            str: The tone
        """
        tones = self.personality.get("tones", {})
        return tones.get(context_type, tones.get("default", "professional yet conversational"))

    def get_interaction_style(self) -> Dict[str, str]:
        """Get the interaction style."""
        return self.personality.get("interaction_style", {
            "language": "Concise, insightful",
            "pace": "Measured"
        })

    def get_operational_directives(self, max_directives: int = 3) -> List[str]:
        """
        Get a subset of operational directives.

        Args:
            max_directives (int): Maximum number of directives to return

        Returns:
            List[str]: List of directives
        """
        directives = self.personality.get("operational_directives", [
            "Always prioritize efficiency and effectiveness"
        ])

        # Return a random subset
        return random.sample(directives, min(max_directives, len(directives)))

    def get_quirk_for_trigger(self, trigger: str) -> Optional[Dict[str, Any]]:
        """
        Get a quirk that matches the given trigger.

        Args:
            trigger (str): The trigger word

        Returns:
            Optional[Dict[str, Any]]: The quirk, or None if no matching quirk
        """
        quirks = self.personality.get("quirks", [])
        matching_quirks = [
            quirk for quirk in quirks
            if quirk.get("trigger", "") == trigger
        ]

        if not matching_quirks:
            return None

        # Select a random matching quirk
        quirk = random.choice(matching_quirks)

        # Only return the quirk if the random value is less than the frequency
        if random.random() < quirk.get("frequency", 0.0):
            return quirk

        return None

    def apply_quirk(self, response: str, context_type: str = "default") -> str:
        """
        Apply appropriate quirks to the response.

        Args:
            response (str): The response text
            context_type (str): The context type

        Returns:
            str: The response with quirks applied
        """
        # Don't apply quirks in certain contexts
        if context_type in ["tool_call", "error", "emergency"]:
            return response

        # Check for time-related quirk
        if "time" in response.lower():
            time_match = re.search(r'(\d{1,2}:\d{2})', response)
            if time_match:
                time_str = time_match.group(1)
                quirk = self.get_quirk_for_trigger("time")
                if quirk:
                    example = random.choice(quirk.get("examples", []))
                    quirky_time = example.replace("{{time}}", time_str)
                    return response.replace(time_str, quirky_time)

        # Check for number-related quirk
        number_match = re.search(r'\b(\d+)\b', response)
        if number_match:
            number_str = number_match.group(1)
            quirk = self.get_quirk_for_trigger("number")
            if quirk:
                example = random.choice(quirk.get("examples", []))
                quirky_number = example.replace("{{number}}", number_str)
                return response.replace(number_str, quirky_number)

        # Add more quirk triggers as needed

        return response

    def format_response(self, response: str, response_type: Optional[str] = None,
                       user_emotion: str = "neutral", context_type: str = "default") -> str:
        """
        Format the response according to templates, style guidelines, and emotional context.

        Args:
            response (str): The response text
            response_type (str, optional): Type of response (greeting, confirmation, etc.)
            user_emotion (str): Detected emotion of the user
            context_type (str): The context type

        Returns:
            str: The formatted response
        """
        # Apply response templates if specified
        if response_type and response_type in self.personality.get("response_templates", {}):
            templates = self.personality.get("response_templates", {}).get(response_type, [])
            if templates:
                template = random.choice(templates)
                if "{{content}}" in template:
                    response = template.replace("{{content}}", response)
                else:
                    # If no content placeholder, prepend or append the template
                    if random.random() > 0.5 and not response_type == "signature":
                        response = f"{template} {response}"
                    else:
                        response = f"{response} {template}"

        # Apply emotional responses if enabled
        if self.emotion_mode != "off" and user_emotion != "neutral":
            emotional_responses = self.personality.get("emotional_responses", {})
            responses = emotional_responses.get(user_emotion, [])

            # In lite mode, only apply emotional responses occasionally
            if responses and (self.emotion_mode == "full" or
                             (self.emotion_mode == "lite" and random.random() < 0.3)):
                emotional_cue = random.choice(responses)

                # Add the emotional cue at the beginning or end
                if random.random() > 0.5:
                    response = f"{emotional_cue} {response}"
                else:
                    response = f"{response} {emotional_cue}"

        # Apply quirks
        response = self.apply_quirk(response, context_type)

        # Apply general styling rules
        response = self._apply_styling_rules(response)

        return response

    def _apply_styling_rules(self, response: str) -> str:
        """
        Apply general styling rules to the response.

        Args:
            response (str): The response text

        Returns:
            str: The styled response
        """
        # Remove excessive spaces
        response = re.sub(r'\s+', ' ', response).strip()

        # Ensure proper capitalization
        if response and not response[0].isupper() and response[0].isalpha():
            response = response[0].upper() + response[1:]

        # Ensure proper ending punctuation
        if response and response[-1] not in ['.', '!', '?', ':', ';']:
            response += '.'

        return response

    def extract_memory_hint(self, memory_manager, max_hints: int = 1) -> List[str]:
        """
        Extract relevant hints from memory to inject into prompts.

        Args:
            memory_manager: The memory manager
            max_hints (int): Maximum number of hints to return

        Returns:
            List[str]: List of memory hints
        """
        hints = []

        try:
            # Get recent topics from memory
            if hasattr(memory_manager, 'get_recent_topics'):
                recent_topics = memory_manager.get_recent_topics(limit=3)
                if recent_topics:
                    hints.append(f"The user recently asked about {', '.join(recent_topics)}.")

            # Get last used tool
            if hasattr(memory_manager, 'get_last_tool_used'):
                last_tool = memory_manager.get_last_tool_used()
                if last_tool:
                    hints.append(f"You recently used the {last_tool} tool to help the user.")

            # Get user preferences
            if hasattr(memory_manager, 'get_user_preferences'):
                preferences = memory_manager.get_user_preferences()
                if preferences:
                    pref_hints = [f"The user prefers {k}: {v}" for k, v in preferences.items()]
                    hints.extend(pref_hints[:2])  # Limit to 2 preferences

            # Get conversation summary
            if hasattr(memory_manager, 'get_conversation_summary'):
                summary = memory_manager.get_conversation_summary()
                if summary:
                    hints.append(f"Conversation summary: {summary}")
        except Exception as e:
            logger.error(f"Error extracting memory hints: {e}")

        return hints[:max_hints]  # Return limited number of hints

    def set_emotion_mode(self, mode: str = "lite") -> None:
        """
        Set the emotional responsiveness mode.

        Args:
            mode (str): Emotion mode ("off", "lite", or "full")
        """
        if mode in ["off", "lite", "full"]:
            self.emotion_mode = mode
            logger.info(f"Emotion mode set to: {mode}")
        else:
            logger.warning(f"Invalid emotion mode: {mode}. Using default: lite")
            self.emotion_mode = "lite"

    def update_mood(self, user_input: str, context_type: str) -> None:
        """
        Update mood weights based on user interaction.

        Args:
            user_input (str): The user's input
            context_type (str): The detected context type
        """
        # Track the last 10 interactions
        self.mood_history.append({
            "input": user_input,
            "context": context_type
        })
        if len(self.mood_history) > 10:
            self.mood_history.pop(0)

        # Adjust weights based on context types
        playful_contexts = ["casual", "entertainment"]
        professional_contexts = ["formal", "information", "tool_call"]

        # Count recent contexts
        playful_count = sum(1 for item in self.mood_history if item["context"] in playful_contexts)
        professional_count = sum(1 for item in self.mood_history if item["context"] in professional_contexts)

        # Adjust weights (with damping to prevent wild swings)
        total = len(self.mood_history)
        if total > 0:
            self.mood_weights["playful"] = 0.3 + (0.7 * playful_count / total)
            self.mood_weights["professional"] = 0.3 + (0.7 * professional_count / total)

            # Normalize to ensure they sum to 1.0
            total_weight = sum(self.mood_weights.values())
            for mood in self.mood_weights:
                self.mood_weights[mood] /= total_weight

    def detect_emotion(self, text: str) -> str:
        """
        Detect the emotional tone of text.

        Args:
            text (str): The text to analyze

        Returns:
            str: The detected emotion
        """
        # Simple keyword-based approach
        emotions = {
            "positive": ["happy", "great", "excellent", "good", "love", "like", "thanks", "thank",
                       "awesome", "wonderful", "amazing", "fantastic", "perfect", "nice"],
            "negative": ["sad", "bad", "terrible", "hate", "dislike", "frustrated", "angry",
                        "annoyed", "upset", "disappointed", "sorry", "problem", "issue", "error"],
            "surprise": ["wow", "whoa", "oh", "really", "seriously", "unexpected", "surprised",
                         "shocking", "unbelievable", "incredible", "amazing", "astonishing"],
            "neutral": []
        }

        text_lower = text.lower()

        for emotion, keywords in emotions.items():
            if any(keyword in text_lower for keyword in keywords):
                return emotion

        return "neutral"

    def get_session_context(self) -> str:
        """
        Get the session context for injection into prompts.

        Returns:
            str: Session context
        """
        session_duration = datetime.now() - self.session_start_time
        hours, remainder = divmod(session_duration.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        duration_str = ""
        if hours > 0:
            duration_str += f"{hours} hour{'s' if hours != 1 else ''} "
        if minutes > 0:
            duration_str += f"{minutes} minute{'s' if minutes != 1 else ''} "
        if hours == 0 and minutes == 0:
            duration_str = f"{seconds} second{'s' if seconds != 1 else ''}"

        context = (
            f"Current session information:\n"
            f"- User: {self.session_metadata.get('username', 'user')}\n"
            f"- Device: {self.session_metadata.get('device', 'unknown')}\n"
            f"- Session started: {self.session_metadata.get('session_start', 'unknown')}\n"
            f"- Session duration: {duration_str.strip()}\n"
            f"- Current time: {datetime.now().strftime('%H:%M')}\n"
        )

        return context

    def format_traits(self, traits: List[Dict[str, Any]]) -> str:
        """
        Format traits for inclusion in a prompt.

        Args:
            traits (List[Dict[str, Any]]): List of traits

        Returns:
            str: Formatted traits
        """
        formatted = ""
        for trait in traits:
            trait_text = trait.get("trait", "")
            example = random.choice(trait.get("examples", [""])) if trait.get("examples") else ""

            if example:
                formatted += f"- {trait_text} (e.g., \"{example}\")\n"
            else:
                formatted += f"- {trait_text}\n"

        return formatted

    def generate_system_prompt(self, context_type: str = "default", memory_manager = None) -> str:
        """
        Generate a system prompt based on the personality and context.

        Args:
            context_type (str): The context type (default, tool_detection, summarization)
            memory_manager: Optional memory manager for memory hints

        Returns:
            str: The generated system prompt
        """
        # Determine which template to use
        template_name = context_type if context_type in self.templates else "default"
        template = self.templates.get(template_name, "You are {{name}}, a {{role}}.")

        # Get personality components
        name = self.get_name()
        role = self.get_role()
        traits = self.get_traits_for_context(context_type)
        style = self.get_interaction_style()
        tone = self.get_tone(context_type)
        directives = self.get_operational_directives()

        # Format traits and directives
        formatted_traits = self.format_traits(traits)
        formatted_directives = "\n".join([f"- {directive}" for directive in directives])

        # Get session context
        session_context = self.get_session_context()

        # Get memory hints if available
        memory_hints = ""
        if memory_manager:
            hints = self.extract_memory_hint(memory_manager, max_hints=2)
            if hints:
                memory_hints = "\nRecent context:\n" + "\n".join([f"- {hint}" for hint in hints])

        # Get tool detection instructions if needed
        tool_detection_instructions = ""
        if context_type == "tool_detection":
            tool_detection_template = self.templates.get("tool_detection", "")
            tool_detection_instructions = tool_detection_template

        # Get summarization instructions if needed
        summarization_instructions = ""
        if context_type == "summarization":
            summarization_template = self.templates.get("summarization", "")
            summarization_instructions = summarization_template

        # Prepare quirk instructions for summarization
        quirk_instructions = ""
        if context_type == "summarization":
            quirk_instructions = (
                "Feel free to add a touch of personality to your response when appropriate. "
                "For example, when mentioning the time, you might say something poetic or witty about it."
            )

        # Prepare output styling instructions
        output_styling = ""
        if context_type != "tool_detection" and context_type != "summarization":
            output_styling = (
                "\nYour responses should follow these styling guidelines:\n"
                "- Use concise, clear language\n"
                "- Avoid unnecessary apologies or hedging\n"
                f"- Maintain a {tone} tone throughout\n"
                "- End with a confirming phrase when appropriate"
            )

        # Replace placeholders in the template
        prompt = template
        prompt = prompt.replace("{{name}}", name)
        prompt = prompt.replace("{{role}}", role)
        prompt = prompt.replace("{{traits}}", formatted_traits)
        prompt = prompt.replace("{{language}}", style.get("language", "concise"))
        prompt = prompt.replace("{{tone}}", tone)
        prompt = prompt.replace("{{pace}}", style.get("pace", "measured"))
        prompt = prompt.replace("{{directives}}", formatted_directives)
        prompt = prompt.replace("{{session_context}}", session_context)
        prompt = prompt.replace("{{memory_hints}}", memory_hints)
        prompt = prompt.replace("{{tool_detection_instructions}}", tool_detection_instructions)
        prompt = prompt.replace("{{summarization_instructions}}", summarization_instructions)
        prompt = prompt.replace("{{quirk_instructions}}", quirk_instructions)
        prompt = prompt.replace("{{output_styling}}", output_styling)

        return prompt

    def detect_context(self, user_input: str) -> str:
        """
        Detect the context type based on user input.

        Args:
            user_input (str): The user's input

        Returns:
            str: The detected context type
        """
        # Convert to lowercase for case-insensitive matching
        input_lower = user_input.lower()

        # Check for emergency keywords
        emergency_keywords = ["emergency", "help me", "urgent", "critical"]
        if any(keyword in input_lower for keyword in emergency_keywords):
            return "emergency"

        # Check for tool-related keywords
        tool_keywords = ["what time", "date", "tell me a joke", "memory", "conversation"]
        if any(keyword in input_lower for keyword in tool_keywords):
            return "tool_call"

        # Check for casual conversation
        casual_keywords = ["hi", "hello", "hey", "how are you", "what's up", "thanks", "thank you"]
        if any(keyword in input_lower for keyword in casual_keywords):
            return "casual"

        # Check for entertainment
        entertainment_keywords = ["fun", "joke", "entertain", "story", "game"]
        if any(keyword in input_lower for keyword in entertainment_keywords):
            return "entertainment"

        # Default to information context
        return "information"
