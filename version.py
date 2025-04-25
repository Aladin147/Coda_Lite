"""
Coda Lite version information.

This module provides version information for the Coda Lite project.
"""

__version__ = "0.1.1-dev"
__version_name__ = "Dashboard Integration"
__version_description__ = "Visual interface for monitoring and interaction"

# Version history
VERSION_HISTORY = {
    "0.0.0": "Initial Prototype",
    "0.0.1": "Personality Engine",
    "0.0.2": "Memory & Tools",
    "0.0.8": "Tool Calling",
    "0.0.9": "Adaptive Agent",
    "0.1.0": "WebSocket Architecture",
    "0.1.1": "Dashboard Integration"
}

def get_version_info():
    """Get version information as a dictionary."""
    return {
        "version": __version__,
        "name": __version_name__,
        "description": __version_description__
    }

def get_version_string():
    """Get formatted version string."""
    return f"v{__version__} - {__version_name__}"

def get_full_version_string():
    """Get full version string with description."""
    return f"Coda Lite v{__version__} ({__version_name__}): {__version_description__}"
