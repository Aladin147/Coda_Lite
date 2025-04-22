# Tools Manifest and Help Command

This document describes the Tools Manifest and Help Command feature in Coda Lite v0.1.1.

## Overview

The Tools Manifest and Help Command feature allows users to discover and learn about the tools available in Coda Lite. It provides a way for users to ask "What can you do?" and get a clean, formatted list of available tools and capabilities.

## Components

### 1. Enhanced Tool Router

The `ToolRouter` class has been enhanced to store additional metadata about each tool:

- **Name**: The name of the tool
- **Description**: A description of what the tool does
- **Parameters**: Information about the parameters the tool accepts
- **Example**: An example of how to use the tool
- **Category**: The category the tool belongs to (e.g., "Time & Date", "Entertainment")
- **Aliases**: Alternative names for the tool

### 2. Tool Metadata Auto-Discovery

The tool registration system now automatically extracts metadata from function signatures and docstrings:

- **Description**: Extracted from the first line of the function's docstring
- **Parameters**: Extracted from the function's signature and parameter descriptions in the docstring
- **Default Values**: Extracted from the function's signature

### 3. Help Tools

Two new tools have been added to help users discover available tools:

#### `list_tools`

Lists all available tools and their descriptions.

**Parameters**:
- `category` (optional): Filter tools by category (e.g., "Time & Date", "Entertainment")
- `format` (optional): Output format ("text", "markdown", or "json")

**Example**: "What tools do you have?"

**Aliases**: "show_tools", "what_can_you_do", "available_tools"

#### `show_capabilities`

Shows what Coda can do and how to interact with it.

**Parameters**:
- `detail_level` (optional): Level of detail to show ("basic", "detailed", or "examples")

**Example**: "What can you do?"

**Aliases**: "capabilities", "what_can_you_do", "help"

### 4. System Prompt Update

The system prompt has been updated to inform users about the help command:

```
When users ask "What can you do?" or "Show me your capabilities", use the show_capabilities tool to display a list of available tools and features.
```

## Tool Categories

Tools are now organized into the following categories:

- **Time & Date**: Tools related to time and date information
- **Entertainment**: Tools for entertainment purposes
- **Memory**: Tools for accessing and managing memory
- **Help**: Tools for discovering and learning about other tools

## Output Formats

The `list_tools` and `describe_tools` functions support three output formats:

### Text Format (default)

```
Available Tools:

Time & Date:
  get_time: Get the current time.
    Example: What time is it?
    Aliases: get_system_time, time, current_time
```

### Markdown Format

```markdown
# Available Tools

## Time & Date

### get_time

Get the current time.

**Example:** What time is it?

**Aliases:** get_system_time, time, current_time
```

### JSON Format

```json
[
  {
    "name": "get_time",
    "description": "Get the current time.",
    "parameters": {},
    "example": "What time is it?",
    "category": "Time & Date",
    "aliases": ["get_system_time", "time", "current_time"]
  }
]
```

## Usage Examples

### Asking for Available Tools

User: "What tools do you have?"

Coda will use the `list_tools` tool to display a list of all available tools.

### Asking for Capabilities

User: "What can you do?"

Coda will use the `show_capabilities` tool to display a description of its capabilities.

### Filtering Tools by Category

User: "What time tools do you have?"

Coda will use the `list_tools` tool with the category parameter set to "Time & Date".

## Implementation Details

### Tool Registration

Tools are registered with additional metadata:

```python
tool_router.register_tool(
    "get_time",
    get_time,
    aliases=["get_system_time", "time", "current_time"],
    category="Time & Date",
    example="What time is it?"
)
```

### Tool Metadata Storage

Tool metadata is stored in the `tool_metadata` dictionary in the `ToolRouter` class:

```python
self.tool_metadata[tool_name] = {
    "name": tool_name,
    "description": description,
    "parameters": parameters,
    "example": example,
    "category": category,
    "aliases": aliases or []
}
```

## Testing

A test script is provided to verify the Tools Manifest and Help Command functionality:

```
python tests/test_tools_manifest.py
```

This script tests the `describe_tools` method, the `list_tools` tool, and the `show_capabilities` tool with various parameters.
