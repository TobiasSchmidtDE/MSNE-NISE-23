import zmq
import csv
import time
from pathlib import Path


def run_data_collector(port=5556, topic="emg_data", output_folder="./data/recordings/"):
    context = zmq.Context()
    subscriber = context.socket(zmq.SUB)
    subscriber.connect(f"tcp://localhost:{port}")
    subscriber.setsockopt_string(zmq.SUBSCRIBE, topic)

    output_folder = Path(output_folder)
    output_folder.mkdir(parents=True, exist_ok=True)
    output_file = output_folder / f"{time.strftime('%Y-%m-%d_%H-%M-%S')}.csv"
    # We always want to create a new file
    # If the file already exists, we do NOT delete it
    # Instead we add a change the name of the file by adding a number at the end
    i = 1
    while output_file.exists():
        output_file = output_folder / f"{time.strftime('%Y-%m-%d_%H-%M-%S')}_{i}.csv"
        i += 1
    # Open the file in append mode because we want to continously add data to it
    with open(output_file, mode="a", newline="") as file:
        writer = csv.writer(file)
        # Check if the file is empty to write header
        file.seek(0, 2)  # Move the cursor to the end of the file
        if file.tell() == 0:
            writer.writerow(["timestamp", "sensor_1", "sensor_2"])  # write header

        # loop to listen to subscriber
        while True:
            # Read messages one by one until there are none left
            num_messages = 0
            while True:
                try:
                    topic, message = subscriber.recv_string().split()
                    num_messages += 1
                    # Write to CSV file
                    writer.writerow([time.time(), *message.split(",")])
                    # Flush the data to the file after each write
                except zmq.Again:
                    # No more messages in the queue
                    break
            file.flush()
            print(f"Saved {num_messages} messages to {output_file}")


if __name__ == "__main__":
    run_data_collector()
