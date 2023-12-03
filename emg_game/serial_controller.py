import zmq
import time
import serial


# Customizable constants
SERIAL_PORT = "COM5"  # Serial port (change this to the correct port for your system)
BAUD_RATE = 512000  # Baud rate for serial communication


def run_serial_controller(port=5556):
    # Initialize serial port
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE)
    ser.flushInput()

    context = zmq.Context()
    publisher = context.socket(zmq.PUB)
    publisher.bind(f"tcp://*:{port}")

    subscriber = context.socket(zmq.SUB)
    subscriber.connect(f"tcp://localhost:{5560}")
    subscriber.setsockopt_string(zmq.SUBSCRIBE, "vibration")

    while True:
        # loop to read the most recent data from the socket / subscribed topic
        try:
            # Read a line (ending in \n) from the serial port
            ser_bytes = ser.readline()

            # Decode bytes to string, removing the trailing newline character
            decoded_bytes = ser_bytes.decode("utf-8").strip()

            # the format of the data "sensor_1,sensor_2", we want "timestamp,sensor_1,sensor_2"
            decoded_bytes = f"{time.time()},{decoded_bytes}"
            # Publish the data on the "emg_data" topic
            publisher.send_string(f"emg_data {decoded_bytes}")
            # print(f"Sent \"{decoded_bytes}\" to data processor")

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

        
        while True:
            try:
                _, message = subscriber.recv_string(flags=zmq.NOBLOCK).split()
                # Send the message to the Arduino via the serial connection
                ser.write((message + '\n').encode())  # Ensure to add a newline character
                print(f"Sent \"{message}\" to Arduino")
            except zmq.Again:
                # No more messages in the queue
                break
        


if __name__ == "__main__":
    run_serial_controller()
