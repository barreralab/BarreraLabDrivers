import serial
import argparse
import threading
from time import sleep

"""Serial monitor utility to emulate an Arduino serial monitor.

This script connects to a serial port and provides an interactive
console to communicate with the device connected to the serial port.
It also prints any incoming data from the serial device.

Courtesy of ChatGPT
"""


# Function to read from the serial device
def read_from_serial(ser):
    while True:
        if ser.in_waiting:
            # Print incoming data from the serial device
            print(ser.readline().decode("utf-8").strip())


# Function to send user input to the serial device
def write_to_serial(ser, line_ending):
    while True:
        # Get user input
        user_input = input("> ")
        # Append line ending based on user choice
        if line_ending == "LF":
            user_input += "\n"
        elif line_ending == "CR":
            user_input += "\r"
        elif line_ending == "CRLF":
            user_input += "\r\n"
        # Send to serial device
        ser.write(user_input.encode("utf-8"))
        # Sleep to allow time for response
        sleep(0.1)


def start_serial_monitor(port, baudrate, line_ending, timeout):
    try:
        with serial.Serial(port, baudrate, timeout=timeout) as ser:
            print(f"Connected to {port} at {baudrate} baud.")
            # Allow serial device to initialize (Arduino takes time to boot)
            sleep(3)
            # Start a thread to handle reading from the serial device
            threading.Thread(target=read_from_serial, args=(ser,), daemon=True).start()
            # Main thread handles user input and writing to serial
            write_to_serial(ser, line_ending)
    except serial.SerialException as e:
        print(f"Error: {e}")


def start_serial_monitor_cli():
    parser = argparse.ArgumentParser(description="Arduino Serial Monitor Utility")
    parser.add_argument(
        "--port", type=str, required=True, help="COM port (e.g., COM3 or /dev/ttyUSB0)"
    )
    parser.add_argument(
        "--baudrate", type=int, default=9600, help="Baud rate (default: 9600)"
    )
    parser.add_argument(
        "--eol",
        choices=["none", "LF", "CR", "CRLF"],
        default="LF",
        help="End of line character to append to input (none, LF, CR, CRLF)",
    )
    parser.add_argument(
        "--timeout", type=float, default=None, help="Read timeout in seconds"
    )

    args = parser.parse_args()
    start_serial_monitor(args.port, args.baudrate, args.eol, args.timeout)
