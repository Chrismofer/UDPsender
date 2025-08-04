"""
Example MicroPython code for Raspberry Pi Pico W
This code creates a WiFi access point and TCP server to receive commands

Save this as main.py on your Raspberry Pi Pico W
"""

import network
import socket
import time
import machine

# LED setup (built-in LED on Pico W)
led = machine.Pin("LED", machine.Pin.OUT)
led_state = False

def create_access_point():
    """Create WiFi access point"""
    ap = network.WLAN(network.AP_IF)
    ap.active(True)
    
    # Configure the access point
    ap.config(
        essid='PicoControl',      # Network name
        password='picocontrol123', # Password (min 8 chars)
        authmode=network.AUTH_WPA_WPA2_PSK
    )
    
    # Wait for AP to become active
    while not ap.active():
        time.sleep(0.1)
    
    print('Access Point created successfully')
    print('Network name: PicoControl')
    print('Password: picocontrol123')
    print('IP configuration:', ap.ifconfig())
    return ap

def handle_command(command):
    """Process received commands and return response"""
    global led_state
    
    command = command.strip().upper()
    print(f'Processing command: {command}')
    
    if command == 'LED_ON':
        led.on()
        led_state = True
        return 'OK: LED turned ON'
    
    elif command == 'LED_OFF':
        led.off() 
        led_state = False
        return 'OK: LED turned OFF'
    
    elif command == 'LED_TOGGLE':
        led_state = not led_state
        if led_state:
            led.on()
            return 'OK: LED turned ON'
        else:
            led.off()
            return 'OK: LED turned OFF'
    
    elif command == 'STATUS':
        led_status = 'ON' if led_state else 'OFF'
        return f'OK: LED is {led_status}'
    
    elif command == 'BLINK':
        # Blink LED 3 times
        for i in range(3):
            led.on()
            time.sleep(0.2)
            led.off()
            time.sleep(0.2)
        return 'OK: LED blinked 3 times'
    
    elif command == 'PING':
        return 'PONG'
    
    elif command == 'RESET':
        return 'OK: Resetting...'
        # Could implement reset logic here
    
    elif command.startswith('DELAY'):
        # Example: DELAY 1000 (delay in milliseconds)
        try:
            parts = command.split()
            if len(parts) == 2:
                delay_ms = int(parts[1])
                time.sleep(delay_ms / 1000.0)
                return f'OK: Delayed {delay_ms}ms'
        except ValueError:
            pass
        return 'ERROR: Invalid delay format (use DELAY <milliseconds>)'
    
    else:
        return f'ERROR: Unknown command "{command}"'

def start_server(ip='169.254.1.1', port=1234):
    """Start UDP server to listen for commands"""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    try:
        server_socket.bind((ip, port))
        print(f'UDP Server listening on {ip}:{port}')
        print('Waiting for UDP packets...')
        
        while True:
            try:
                # Receive UDP packet
                data, client_addr = server_socket.recvfrom(1024)
                
                if data:
                    # Process command
                    command = data.decode('utf-8').strip()
                    print(f'Received from {client_addr}: "{command}"')
                    
                    response = handle_command(command)
                    
                    # Send response back to client
                    server_socket.sendto(response.encode('utf-8'), client_addr)
                    print(f'Sent to {client_addr}: "{response}"')
                    
                    # Special handling for reset command
                    if command.upper() == 'RESET':
                        time.sleep(0.1)
                        machine.reset()
            
            except Exception as e:
                print(f'Error handling UDP packet: {e}')
    
    except Exception as e:
        print(f'UDP Server error: {e}')
    finally:
        server_socket.close()
        print('UDP Server socket closed')

def main():
    """Main function"""
    print('Starting Raspberry Pi Pico WiFi Controller...')
    
    # Turn off LED initially
    led.off()
    
    # Create access point
    ap = create_access_point()
    
    # Start server
    try:
        start_server()
    except KeyboardInterrupt:
        print('Server stopped by user')
    except Exception as e:
        print(f'Server crashed: {e}')
    
    # Cleanup
    ap.active(False)
    print('Access point deactivated')

# Run the main function
if __name__ == '__main__':
    main()
