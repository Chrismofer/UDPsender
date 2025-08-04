"""
Configuration file for UDPsender
"""

# Default connection settings
DEFAULT_DEVICE_IP = "169.254.1.1"  # Default device IP
DEFAULT_DEVICE_PORT = 1234

# Connection settings
CONNECTION_TIMEOUT = 5  # seconds
RESPONSE_TIMEOUT = 1    # seconds
BUFFER_SIZE = 1024      # bytes

# GUI settings
WINDOW_WIDTH = 600
WINDOW_HEIGHT = 500
LOG_HEIGHT = 15
FONT_FAMILY = "Consolas"
FONT_SIZE = 10

# Example commands for device operations
EXAMPLE_COMMANDS = [
    "/1/T",
    "/2/T", 
    "/2/O",
    "/2/500",
    "/2/-12000",
    "/1/200",
]

# Application information
APP_NAME = "UDPsender"
APP_VERSION = "v1.1"
APP_AUTHOR = "Chris Bovee"

