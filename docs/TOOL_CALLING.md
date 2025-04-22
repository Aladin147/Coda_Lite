# Tool Calling System in Coda Lite

## Overview

Coda Lite implements a two-pass tool calling system that allows the assistant to:
1. Detect when a tool needs to be called
2. Execute the appropriate tool
3. Process the tool result
4. Generate a natural language response

## Current Implementation (v0.1.0)

The current implementation follows this flow:
1. User input is sent to the LLM with a system prompt that includes tool descriptions
2. The LLM generates a response, potentially including a tool call in JSON format
3. If a tool call is detected, the system:
   - Extracts the tool name and arguments
   - Executes the appropriate tool
   - Formats the result in natural language
   - Sends the result to the LLM in a second pass with a clean context
   - Applies JSON cleaning to the final response

## Supported Tools

The current version supports the following tools:
- `get_time`: Returns the current time
- `get_date`: Returns the current date
- `tell_joke`: Returns a random joke
- `list_memory_files`: Lists available memory files
- `count_conversation_turns`: Counts the number of turns in the current conversation

## Known Issues

### JSON Leakage (To Fix in v0.1.1)

**Issue**: Despite multiple layers of cleaning and a two-pass approach, JSON from the tool call sometimes leaks into the final response.

**Current Behavior**: When asking for the time, the response might include both the JSON tool call and the natural language response:
```
{"tool_call": { "name": "get_time", "args": {} }}
The current time is 03:34:22
```

**Attempted Solutions**:
1. Implemented a two-pass approach with a clean context
2. Added aggressive JSON cleaning with regex patterns
3. Updated system prompts to explicitly forbid JSON in responses
4. Added direct fallbacks for common tools
5. Enhanced error handling and logging

**Next Steps**:
- Investigate alternative LLM prompting techniques
- Consider implementing a more robust JSON parser
- Explore model fine-tuning to reduce JSON leakage
- Test with different LLM models to see if the issue persists

## Future Improvements

1. **Tool Chaining**: Allow tools to use the results of other tools
2. **More Complex Tools**: Add tools for weather, calculations, web search, etc.
3. **Improved Error Handling**: Better fallbacks and error messages
4. **Performance Optimization**: Reduce latency in the two-pass approach
5. **Caching**: Implement caching for frequently used tool results

## Implementation Details

The tool calling system is implemented across several files:
- `main.py`: Contains the main processing logic
- `llm/ollama_llm.py`: Handles LLM interactions
- `tools/tool_router.py`: Routes tool calls to the appropriate handlers
- `tools/basic_tools.py`: Implements the basic tools

## Development History

- v0.0.7: Initial implementation of tool calling
- v0.0.8: Added JSON cleaning and improved prompts
- v0.0.9: Fixed issues with the OllamaLLM chat method
- v0.1.0: Enhanced JSON cleaning and improved error handling
