<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# UDPsender Project

This is a Python GUI application for sending UDP commands to any network device. When working on this project:

## Project Context
- **Target Device**: Any device that can receive UDP packets
- **Communication**: UDP socket communication over network
- **GUI Framework**: tkinter (Python standard library)
- **Network Setup**: Device accessible over IP network

## Code Guidelines
- Use tkinter for GUI components with ttk for modern styling
- Implement proper error handling for network operations
- Include connection timeouts and graceful disconnection
- Log all network operations with timestamps
- Follow Python PEP 8 style guidelines
- Use type hints where appropriate

## Key Components
- **main.py**: Main GUI application with UDPSender class
- **config.py**: Configuration constants and settings
- **Socket Communication**: Non-blocking UDP communication
- **Error Handling**: User-friendly error messages and logging

## Network Communication
- Default IP: 169.254.1.1 (configurable)
- Default Port: 1234
- Protocol: UDP with UTF-8 text commands
- Timeout handling for both connection and responses

## Testing Considerations
- Test with actual Pico hardware when possible
- Include mock/simulation capabilities for development
- Handle network disconnections gracefully
- Validate user input (IP addresses, ports, commands)

## Future Enhancements
- Consider adding HTTP REST API support
- Potential for data visualization
- Command history and favorites
- Multiple device management
- Device discovery and auto-configuration
