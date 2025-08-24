# UDPsender

A Python GUI for controlling a device over UDP. This application provides a simple interface to send text commands to a chosen IP and port.

## Quick Start

1. **Start the Application**:
   python main.py

2. **Configure Connection**:
   - Enter the device's IP address (default: 169.254.1.1)
   - Enter the port number (default: 1234)
   - Click "Connect"

3. **Send Commands**:
   - Type commands in the command input box
   - Press Enter or click "Send"
   - View responses in the log area

4. **Manage Logs**:
   - Click "Clear Log" to clear the display
   - Click "Save Log" to save the session to a file


## Installation / Setup

### Windows

1. **Install Python 3.6+**:
   - Download from [python.org](https://www.python.org/downloads/)
   - During installation, check "Add Python to PATH"

2. **Download UDPsender**:
   ```cmd
   git clone https://github.com/Chrismofer/UDPsender.git
   cd UDPsender
   ```

3. **Run the application**:
   ```cmd
   python main.py
   ```

### Ubuntu/Debian Linux

1. **Install dependencies**:
   ```bash
   sudo apt update
   sudo apt install python3 python3-tk python3-pip git
   ```

2. **Download UDPsender**:
   ```bash
   git clone https://github.com/Chrismofer/UDPsender.git
   cd UDPsender
   ```

3. **Run the application**:
   ```bash
   python3 main.py
   ```

### macOS

1. **Install Python 3.6+**:
   - Using Homebrew: `brew install python-tk`
   - Or download from [python.org](https://www.python.org/downloads/)

2. **Download UDPsender**:
   ```bash
   git clone https://github.com/Chrismofer/UDPsender.git
   cd UDPsender
   ```

3. **Run the application**:
   ```bash
   python3 main.py
   ```

### Alternative: Direct Download
If you don't have Git, download the ZIP file from the [GitHub repository](https://github.com/Chrismofer/UDPsender), extract it, and run `python main.py` from the extracted folder.


### Target Device Requirements

Your target device should be:
- Accessible over the network (WiFi, Ethernet, etc.)
- Running a UDP server listening for packets
- Configured to listen on a specific IP address and port (default: 169.254.1.1:1234)
- Optionally able to send UDP responses back

## Project Structure

UDPsender/
├── main.py              # Main GUI application
├── config.py            # Configuration constants
├── requirements.txt     # Python dependencies (minimal)
├── README.md           # This file
├── pico_example.py     # Example device code (Raspberry Pi Pico)
└── .github/
    └── copilot-instructions.md


### Troubleshooting
1. **Connection Failed**:
   - Ensure your computer can reach the target device's network
   - Verify the IP address and port number
   - Check that the device is running and accessible
   - Try pinging the device in your command prompt: `ping 169.254.1.1`

2. **No Response**:
   - The device might not be programmed to send responses
   - Check the device's logs for debugging
   - UDP is connectionless, so one-way communication is normal

3. **Network Issues**:
   - Check network connectivity
   - Verify firewall settings (Windows Defender, ufw, etc.)
   - Ensure the device's UDP server is running correctly

**Windows:**
- If tkinter is missing, reinstall Python with "tcl/tk and IDLE" option checked
- Windows Firewall may block the application - add an exception if needed

**Linux:**
- If tkinter is missing: `sudo apt install python3-tk`
- If permission errors: `chmod +x main.py`
- For headless systems: GUI requires X11 forwarding or local display

**macOS:**
- If tkinter issues: `brew install python-tk`
- May need to install Xcode command line tools: `xcode-select --install`ice and receive responses over UDP protocol.DP Device Controller

## Example Device Code (Raspberry Pi Pico)

Here's a basic MicroPython example for a Raspberry Pi Pico to create a WiFi access point and UDP server:

```python
import network
import socket
import time

# Create access point
ap = network.WLAN(network.AP_IF)
ap.active(True)
ap.config(essid='PicoControl', password='12345678')

print('Access Point created')
print('Network config:', ap.ifconfig())

# Create UDP socket server
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind(('169.254.1.1', 1234))

print('UDP Server listening on 169.254.1.1:1234')

while True:
    try:
        data, client_addr = server_socket.recvfrom(1024)
        
        if data:
            command = data.decode('utf-8').strip()
            print(f'Received from {client_addr}: {command}')
            
            # Process command here
            response = f"OK: {command}"
            server_socket.sendto(response.encode('utf-8'), client_addr)
            print(f'Sent response: {response}')
            
    except Exception as e:
        print(f'Error: {e}')
```

## Default Settings

- **Default IP**: 169.254.1.1
- **Default Port**: 1234
- **Protocol**: UDP
- **Connection Timeout**: 5 seconds
- **Response Timeout**: 1 second

## License

This project is open source and available under the MIT License.
