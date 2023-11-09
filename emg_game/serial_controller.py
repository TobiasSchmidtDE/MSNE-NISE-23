import zmq
import time
import serial


# Customizable constants
SERIAL_PORT = "COM9"  # Serial port (change this to the correct port for your system)
BAUD_RATE = 512000  # Baud rate for serial communication


def run_serial_controller(port=5556):
    # Initialize serial port
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE)
    ser.flushInput()

    context = zmq.Context()
    publisher = context.socket(zmq.PUB)
    publisher.bind(f"tcp://*:{port}")

    while True:
        try:
            # Read a line (ending in \n) from the serial port
            ser_bytes = ser.readline()

            # Decode bytes to string, removing the trailing newline character
            decoded_bytes = ser_bytes.decode("utf-8").strip()

            # print(f"Serial controller sends data: {decoded_bytes}")

            # Publish the data on the "emg_data" topic
            publisher.send_string(f"emg_data {decoded_bytes}")

        except serial.SerialException as e:
            print(f"Serial error: {e}")
            # Handle the error or wait before retrying
            time.sleep(2)
        except KeyboardInterrupt:
            print("Serial controller terminated by user")
            break
        except Exception as e:
            print(f"Unexpected error: {e}")
            break


if __name__ == "__main__":
    run_serial_controller()
