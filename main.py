#!/usr/bin/env python3
"""
UDPsender
A GUI application to send commands to a device over UDP.

Version 1.1 by Chris Bovee
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import socket
import threading
import time
from datetime import datetime

from config import APP_NAME, APP_VERSION, APP_AUTHOR


class UDPSender:
    # Constants
    DEFAULT_IP = "169.254.1.1"
    DEFAULT_PORT = 1234
    CONNECTION_TIMEOUT = 5
    RESPONSE_TIMEOUT = 1
    BUFFER_SIZE = 1024
    
    # UI Constants
    WINDOW_SIZE = "600x500"
    LOG_FONT = ("Consolas", 9)
    COMMAND_FONT = ("Consolas", 10)
    
    # Status colors
    CONNECTED_COLOR = "green"
    DISCONNECTED_COLOR = "red"
    
    def __init__(self, root):
        self.root = root
        self.root.title("UDPsender")
        self.root.geometry(self.WINDOW_SIZE)
        
        self.is_connected = False
        self.udp_socket = None
        self.target_address = None
        self.connection_animation_active = False
        
        self._create_ui()
        self._log_startup_message()
        
    def _create_ui(self):
        main_container = self._create_main_container()
        
        connection_frame = self._create_connection_section(main_container)
        command_frame = self._create_command_section(main_container)
        log_frame = self._create_log_section(main_container)
        button_frame = self._create_control_buttons(main_container)
        
    def _create_main_container(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        return main_frame
        
    def _create_connection_section(self, parent):
        connection_frame = ttk.LabelFrame(parent, text="Connection Settings", padding="5")
        connection_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        connection_frame.columnconfigure(1, weight=1)
        
        self._create_ip_input(connection_frame)
        self._create_port_input(connection_frame)
        self._create_connection_button(connection_frame)
        self._create_status_display(connection_frame)
        
        return connection_frame
    
    def _create_ip_input(self, parent):
        ttk.Label(parent, text="IP Address:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.ip_address_var = tk.StringVar(value=self.DEFAULT_IP)
        self.ip_address_entry = ttk.Entry(parent, textvariable=self.ip_address_var, width=15)
        self.ip_address_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
    
    def _create_port_input(self, parent):
        ttk.Label(parent, text="Port:").grid(row=0, column=2, sticky=tk.W, padx=(10, 5))
        self.port_number_var = tk.StringVar(value=str(self.DEFAULT_PORT))
        self.port_number_entry = ttk.Entry(parent, textvariable=self.port_number_var, width=8)
        self.port_number_entry.grid(row=0, column=3, sticky=tk.W)
    
    def _create_connection_button(self, parent):
        self.connection_toggle_button = ttk.Button(parent, text="Connect", command=self._toggle_connection)
        self.connection_toggle_button.grid(row=0, column=4, padx=(10, 0))
    
    def _create_status_display(self, parent):
        self.connection_status_var = tk.StringVar(value="Disconnected")
        self.connection_status_label = ttk.Label(parent, textvariable=self.connection_status_var, 
                                                foreground=self.DISCONNECTED_COLOR)
        self.connection_status_label.grid(row=1, column=0, columnspan=5, pady=(5, 0))
    
    def _create_command_section(self, parent):
        command_frame = ttk.LabelFrame(parent, text="Command Input", padding="5")
        command_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        command_frame.columnconfigure(0, weight=1)
        
        self.command_text_var = tk.StringVar()
        self.command_input_entry = ttk.Entry(command_frame, textvariable=self.command_text_var, 
                                           font=self.COMMAND_FONT)
        self.command_input_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        self.command_input_entry.bind('<Return>', lambda e: self._send_command())
        
        self.send_command_button = ttk.Button(command_frame, text="Send", command=self._send_command, 
                                            state="disabled")
        self.send_command_button.grid(row=0, column=1)
        
        return command_frame
    
    def _create_log_section(self, parent):
        log_frame = ttk.LabelFrame(parent, text="Response Log", padding="5")
        log_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        self.response_log_display = scrolledtext.ScrolledText(log_frame, height=15, width=70, 
                                                            font=self.LOG_FONT)
        self.response_log_display.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        return log_frame
    
    def _create_control_buttons(self, parent):
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # Left side buttons
        ttk.Button(button_frame, text="Save Log", command=self._save_log).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Clear Log", command=self._clear_log).pack(side=tk.LEFT)
        
        # Right side About button
        ttk.Button(button_frame, text="About", command=self._show_about).pack(side=tk.RIGHT)
        
        return button_frame
    
    def _log_startup_message(self):
        self._add_log_entry("Application started. Enter device IP address and port, then click Connect.")
    
    def _toggle_connection(self):
        if not self.is_connected:
            self._establish_connection()
        else:
            self._close_connection()
    
    def _establish_connection(self):
        try:
            target_ip = self._get_validated_ip()
            target_port = self._get_validated_port()
            
            # Start connection animation
            self._start_connection_animation()
            
            # Run connection in separate thread to keep UI responsive
            connection_thread = threading.Thread(
                target=self._connect_in_background,
                args=(target_ip, target_port)
            )
            connection_thread.daemon = True  # Compatible with Python 3.0+
            connection_thread.start()
            
        except ValueError as e:
            messagebox.showerror("Error", str(e))
    
    def _start_connection_animation(self):
        self.connection_animation_active = True
        self.connection_toggle_button.config(state="disabled")
        animation_thread = threading.Thread(target=self._animate_connection_dots)
        animation_thread.daemon = True  # Compatible with Python 3.0+
        animation_thread.start()
    
    def _animate_connection_dots(self):
        base_message = "Trying to connect"
        dots = ""
        
        while self.connection_animation_active:
            # Update the log with animated dots
            current_message = "{0}{1}".format(base_message, dots)
            
            # Use after() to safely update GUI from thread
            self.root.after(0, lambda msg=current_message: self._update_connection_status(msg))
            
            # Add another dot (max 5 dots, then reset)
            dots += "."
            if len(dots) > 5:
                dots = ""
            
            time.sleep(1)  # Wait 1 second between dots
    
    def _update_connection_status(self, message):
        # Update the status label with the animated message
        if self.connection_animation_active:
            self.connection_status_var.set(message)
    
    def _stop_connection_animation(self):
        self.connection_animation_active = False
        self.connection_toggle_button.config(state="normal")
    
    def _connect_in_background(self, target_ip, target_port):
        try:
            # Add initial log entry
            self.root.after(0, lambda: self._add_log_entry("Setting up UDP connection to {0}:{1}...".format(target_ip, target_port)))
            
            self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.udp_socket.settimeout(self.CONNECTION_TIMEOUT)
            self.target_address = (target_ip, target_port)
            
            connection_successful = self._test_connection_with_ping()
            
            # Update UI on main thread
            self.root.after(0, lambda: self._finalize_connection(target_ip, target_port, connection_successful))
            
        except socket.timeout:
            self.root.after(0, self._handle_connection_timeout)
        except socket.error as e:
            self.root.after(0, lambda: self._handle_socket_error(e))
        except Exception as e:
            self.root.after(0, lambda: self._handle_unexpected_error(e))
    
    def _get_validated_ip(self):
        ip_address = self.ip_address_var.get().strip()
        if not ip_address:
            raise ValueError("Please enter an IP address")
        return ip_address
    
    def _get_validated_port(self):
        try:
            return int(self.port_number_var.get().strip())
        except ValueError:
            raise ValueError("Port must be a valid number")
    
    def _test_connection_with_ping(self):
        ping_message = "PING"
        self.udp_socket.sendto(ping_message.encode('utf-8'), self.target_address)
        
        try:
            response_data, sender_address = self.udp_socket.recvfrom(self.BUFFER_SIZE)
            response_text = response_data.decode('utf-8')
            self.root.after(0, lambda: self._add_log_entry("Connection test successful: {0}".format(response_text)))
            return True
        except socket.timeout:
            self.root.after(0, lambda: self._add_log_entry("No response to ping, but UDP socket is ready"))
            return False
    
    def _finalize_connection(self, target_ip, target_port, connection_successful):
        self._stop_connection_animation()
        self._update_ui_for_connected_state()
        self._add_log_entry("UDP connection ready for {0}:{1}".format(target_ip, target_port))
    
    def _update_ui_for_connected_state(self):
        self.is_connected = True
        self.connection_status_var.set("Connected (UDP)")
        self.connection_status_label.config(foreground=self.CONNECTED_COLOR)
        self.connection_toggle_button.config(text="Disconnect")
        self.send_command_button.config(state="normal")
        self.command_input_entry.focus()
    
    def _handle_connection_timeout(self):
        self._stop_connection_animation()
        self._add_log_entry("Connection timeout - check IP address and ensure device is accessible")
        messagebox.showerror("Connection Error", "Connection timeout")
    
    def _handle_socket_error(self, error):
        self._stop_connection_animation()
        self._add_log_entry("Connection failed: {0}".format(error))
        messagebox.showerror("Connection Error", "Failed to connect: {0}".format(error))
    
    def _handle_unexpected_error(self, error):
        self._stop_connection_animation()
        self._add_log_entry("Unexpected error: {0}".format(error))
        messagebox.showerror("Error", "Unexpected error: {0}".format(error))
    
    def _close_connection(self):
        # Stop any active connection animation
        self._stop_connection_animation()
        
        try:
            if self.udp_socket:
                self.udp_socket.close()
                self.udp_socket = None
            
            self._update_ui_for_disconnected_state()
            self._add_log_entry("Disconnected from device")
            
        except Exception as e:
            self._add_log_entry("Error during disconnection: {0}".format(e))
    
    def _update_ui_for_disconnected_state(self):
        self.is_connected = False
        self.connection_status_var.set("Disconnected")
        self.connection_status_label.config(foreground=self.DISCONNECTED_COLOR)
        self.connection_toggle_button.config(text="Connect")
        self.send_command_button.config(state="disabled")
    
    def _send_command(self):
        if not self._validate_connection():
            return
        
        command_text = self._get_command_text()
        if not command_text:
            return
        
        try:
            self._transmit_command(command_text)
            self._add_log_entry("Sent: {0}".format(command_text))
            self._attempt_to_receive_response()
            self._clear_command_input()
            
        except socket.error as e:
            self._handle_send_error(e)
        except Exception as e:
            self._add_log_entry("Unexpected error: {0}".format(e))
    
    def _validate_connection(self):
        if not self.is_connected or not self.udp_socket:
            messagebox.showerror("Error", "Not connected to device")
            return False
        return True
    
    def _get_command_text(self):
        return self.command_text_var.get().strip()
    
    def _transmit_command(self, command_text):
        encoded_message = command_text.encode('utf-8')
        self.udp_socket.sendto(encoded_message, self.target_address)
    
    def _attempt_to_receive_response(self):
        self.udp_socket.settimeout(self.RESPONSE_TIMEOUT)
        try:
            response_data, sender_address = self.udp_socket.recvfrom(self.BUFFER_SIZE)
            response_text = response_data.decode('utf-8').strip()
            if response_text:
                self._add_log_entry("Response: {0}".format(response_text))
        except socket.timeout:
            pass  # No response received, which is normal for UDP
    
    def _clear_command_input(self):
        self.command_text_var.set("")
    
    def _handle_send_error(self, error):
        self._add_log_entry("Send failed: {0}".format(error))
        messagebox.showerror("Send Error", "Failed to send command: {0}".format(error))
        self._close_connection()
    
    def _add_log_entry(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_entry = "[{0}] {1}\n".format(timestamp, message)
        
        self.response_log_display.insert(tk.END, formatted_entry)
        self.response_log_display.see(tk.END)
    
    def _clear_log(self):
        self.response_log_display.delete(1.0, tk.END)
    
    def _save_log(self):
        try:
            filename = self._get_save_filename()
            if filename:
                self._write_log_to_file(filename)
                self._add_log_entry("Log saved to {0}".format(filename))
        except Exception as e:
            messagebox.showerror("Save Error", "Failed to save log: {0}".format(e))
    
    def _get_save_filename(self):
        return filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            title="Save Log File"
        )
    
    def _write_log_to_file(self, filename):
        with open(filename, 'w') as file:
            file.write(self.response_log_display.get(1.0, tk.END))
    
    def _show_about(self):
        about_window = tk.Toplevel(self.root)
        about_window.title("About {0}".format(APP_NAME))
        about_window.geometry("250x120")
        about_window.resizable(False, False)
        
        # Center the window on screen
        about_window.update_idletasks()  # Ensure window size is calculated
        screen_width = about_window.winfo_screenwidth()
        screen_height = about_window.winfo_screenheight()
        window_width = 250
        window_height = 120
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        about_window.geometry("{0}x{1}+{2}+{3}".format(window_width, window_height, x, y))
        
        about_window.transient(self.root)
        about_window.grab_set()
        
        # About content
        about_frame = ttk.Frame(about_window, padding="20")
        about_frame.pack(fill=tk.BOTH, expand=True)
        
        # App name and version on same line
        title_frame = ttk.Frame(about_frame)
        title_frame.pack(pady=(0, 5))
        ttk.Label(title_frame, text=APP_NAME, font=("Arial", 12, "bold")).pack(side=tk.LEFT)
        ttk.Label(title_frame, text=" {0}".format(APP_VERSION), font=("Arial", 12)).pack(side=tk.LEFT)
        
        ttk.Label(about_frame, text="by {0}".format(APP_AUTHOR)).pack(pady=(0, 15))
        
        ttk.Button(about_frame, text="OK", command=about_window.destroy).pack()
    
    def handle_application_closing(self):
        if self.is_connected:
            self._close_connection()
        self.root.destroy()


def main():
    root = tk.Tk()
    app = UDPSender(root)
    
    root.protocol("WM_DELETE_WINDOW", app.handle_application_closing)
    root.mainloop()


if __name__ == "__main__":
    main()
