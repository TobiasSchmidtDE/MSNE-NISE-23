import zmq
import time
import serial
import numpy as np
import pandas as pd
from pathlib import Path
from tqdm import tqdm

SERIAL_FAKE_HZ = 10


def run_mock_serial_controller(recording: Path):
    context = zmq.Context()
    publisher = context.socket(zmq.PUB)
    publisher.bind(f"tcp://*:{5556}")
    # open the file and load the whole thing into memory
    with open(recording, mode="r", newline="") as file:
        # file is a csv file with the following format:
        # timestamp,sensor_1,sensor_2
        # read the file
        df = pd.read_csv(file)
    df.reset_index(inplace=True)
    df["time_diff"] = df["timestamp"].diff()
    df["time_diff"].iloc[0] = 0
    df["time_cumsum"] = df["time_diff"].cumsum()

    time_start = time.time()
    last_index = 0
    pbar = tqdm(total=len(df))
    while True:
        time_passed = time.time() - time_start

        # get the rows after the last index and before the current time (time_passed & time_cumsum)
        data_mask = (df["index"] > last_index) & (df["time_cumsum"] <= time_passed)
        if sum(data_mask) == 0:
            # no new data
            # maybe sleep for a bit?
            time.sleep(1 / SERIAL_FAKE_HZ)
            continue

        # print(f"Sending {sum(data_mask)} data points")
        data_to_send = df[data_mask].copy()

        data_to_send["new_timestamp"] = data_to_send["time_cumsum"] + time_start

        for _, row in data_to_send.iterrows():
            # the format should be "timestamp,sensor_1,sensor_2"
            message = f"{row['new_timestamp']},{row['sensor_1']},{row['sensor_2']}"
            # Publish the data on the "emg_data" topic
            publisher.send_string(f"emg_data {message}")

        # this gets the index of the last row that is True in the mask (e.g. the last data point that will be sent)
        last_index = len(data_mask) - data_mask[::-1].argmax() - 1

        pbar.update(sum(data_mask))
        # finally check whether we have reached the end of the file and reset the time_start and last_index
        if last_index >= len(df) - 1:
            print("Reached the end of the file, resetting")
            time_start = time.time()
            last_index = 0
            pbar.reset()
            # maybe sleep for a bit?
            time.sleep(1 / 100)


if __name__ == "__main__":
    run_mock_serial_controller(recording=str(Path("data/recordings/2023-11-15_21-15-09.csv")))
