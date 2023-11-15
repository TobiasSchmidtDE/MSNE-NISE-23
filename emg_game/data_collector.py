import zmq
import csv
import time
from pathlib import Path


def run_data_collector(port=5556, output_folder="./data/recordings/"):
    context = zmq.Context()
    subscriber = context.socket(zmq.SUB)
    subscriber.connect(f"tcp://localhost:{port}")
    subscriber.setsockopt_string(zmq.SUBSCRIBE, "emg_data")

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
                    _, message = subscriber.recv_string().split()
                    num_messages += 1
                    # Write to CSV file
                    writer.writerow([*message.split(",")])
                    # Flush the data to the file after each write
                except zmq.Again:
                    # No more messages in the queue
                    break
            file.flush()
            print(f"Saved {num_messages} messages to {output_file}")


def run_labeled_data_collector(output_folder="./data/recordings_labeled/"):
    context = zmq.Context()
    subscriber_emg_data = context.socket(zmq.SUB)
    subscriber_emg_data.connect(f"tcp://localhost:{5556}")
    subscriber_emg_data.setsockopt_string(zmq.SUBSCRIBE, "emg_data")

    subscriber_label_data = context.socket(zmq.SUB)
    subscriber_label_data.connect(f"tcp://localhost:{5557}")
    subscriber_label_data.setsockopt_string(zmq.SUBSCRIBE, "label_data")

    output_folder = Path(output_folder)
    recording_folder = output_folder / f"{time.strftime('%Y-%m-%d_%H-%M-%S')}/"
    # We always want to create a new folder
    # If the file already exists, we do NOT delete it
    # Instead we add a change the name of the file by adding a number at the end
    i = 1
    while recording_folder.exists():
        recording_folder = output_folder / f"{time.strftime('%Y-%m-%d_%H-%M-%S')}_{i}/"
        i += 1

    recording_folder.mkdir(parents=True, exist_ok=True)
    label_file_path = recording_folder / "labels.csv"
    data_file_path = recording_folder / "data.csv"
    print(f"Saving data to {recording_folder}")
    # Open the file in append mode because we want to continously add data to it
    with open(label_file_path, mode="a", newline="") as label_file, open(
        data_file_path, mode="a", newline=""
    ) as data_file:
        label_writer = csv.writer(label_file)
        data_writer = csv.writer(data_file)
        label_writer.writerow(["timestamp", "label_left", "label_right"])
        data_writer.writerow(["timestamp", "sensor_1", "sensor_2"])

        # loop to listen to subscriber
        while True:
            # print("listening to subscribers")
            # Read messages one by one until there are none left
            while True:
                # print("trying to read emg")
                try:
                    _, message = subscriber_emg_data.recv_string(
                        flags=zmq.NOBLOCK
                    ).split()
                    # write to data file
                    data_writer.writerow([*message.split(",")])
                except zmq.Again:
                    # No more messages in the queue
                    break

            while True:
                # print("trying to read label")
                try:
                    _, message = subscriber_label_data.recv_string(
                        flags=zmq.NOBLOCK
                    ).split()
                    # write to data file
                    print("read label_data:", message)
                    label_writer.writerow([*message.split(",")])
                except zmq.Again:
                    # No more messages in the queue
                    # print("no more messages for label data")
                    break

            data_file.flush()
            label_file.flush()


if __name__ == "__main__":
    run_data_collector()
