import zmq
import csv
import time


def run_data_collector(port=5556, topic="emg_data", output_file="./data/emg_data.csv"):
    context = zmq.Context()
    subscriber = context.socket(zmq.SUB)
    subscriber.connect(f"tcp://localhost:{port}")
    subscriber.setsockopt_string(zmq.SUBSCRIBE, topic)

    # Open the CSV file in append mode, which will create the file if it doesn't exist
    # and will append to the end of the file if it does exist.
    with open(output_file, mode="a", newline="") as file:
        writer = csv.writer(file)
        # Check if the file is empty to write header
        file.seek(0, 2)  # Move the cursor to the end of the file
        if file.tell() == 0:
            writer.writerow(["timestamp", "sensor_1", "sensor_2"])  # write header

        while True:
            # Receive a message
            topic, message = subscriber.recv_string().split()

            # Write to CSV file
            writer.writerow([time.time(), *message.split(",")])
            # Flush the data to the file after each write
            file.flush()


if __name__ == "__main__":
    run_data_collector()
