import zmq
import csv
import time
from pathlib import Path
import numpy as np
from tqdm import tqdm

def onset_detection():
    context = zmq.Context()
    subscriber = context.socket(zmq.SUB)
    subscriber.connect(f"tcp://localhost:{5556}")
    subscriber.setsockopt_string(zmq.SUBSCRIBE, "emg_data")

    # Publisher to send commands to pygame
    threshold_publisher = context.socket(zmq.PUB)
    threshold_publisher.bind(f"tcp://*:{5558}")

    # Publisher to send commands to pygame
    vibrate_publisher = context.socket(zmq.PUB)
    vibrate_publisher.bind(f"tcp://*:{5560}")

    last_vibrate_sensor_1 = 0
    last_vibrate_sensor_2 = 0
    vibrate_dely = 0.5 # s

    window_size_mean = 50
    window_size_std = 500

    np_data = None
    finished_calibraton = False
    calibrated_std = np.inf
    # add pbar for calibaration progress bar
    pbar = tqdm(total=max(window_size_mean, window_size_std))
    # loop to process the data
    while True:
        # loop to read the most recent data from the socket / subscribed topic
        new_data = []
        while True:
            try:
                _, message = subscriber.recv_string(flags=zmq.NOBLOCK).split()
                timestamp, sensor_1, sensor_2 = message.split(",")
                new_data += [[float(timestamp), float(sensor_1), float(sensor_2)] ]
            except zmq.Again:
                # No more messages in the queue
                break
        if len(new_data) == 0:
            # no new data
            # maybe sleep for a bit?
            time.sleep(1 / 100)
            continue
        if not finished_calibraton:
            pbar.update(len(new_data))
        np_new_data = np.array(new_data)
        if np_data is None:
            np_data = np_new_data
        else:
            np_data = np.vstack([np_data, np_new_data])
        
        # create a view of np data for the sensor data (not the timestamp)
        sensor_data = np_data[:, 1:]
        new_sensor_data = np_new_data[:, 1:]
        # only start processing when we have enough data
        if np_data.shape[0] > max(window_size_mean, window_size_std):
            if not finished_calibraton:
                print("Finished calibration")
                calibrated_std = np.std(sensor_data[-window_size_std:], axis=0)
                finished_calibraton = True
                pbar.close()
            # calculate the mean and std of the data
            mean = np.mean(sensor_data[-window_size_mean:], axis=0)
            
            # calculate the threshold
            threshold = mean + 8 * calibrated_std


            # detect spike if the last value is more than 3 stds away from the mean
            # there are len(new_data) values in the new data, each of which have to be checked against the mean and std
            onset_detected = new_sensor_data > threshold
            # get the timestamp of the onsets 
            onset_timestamps_1 = np_new_data[onset_detected[:, 0], 0]
            onset_timestamps_2 = np_new_data[onset_detected[:, 1], 0]

            # check if any of the values in the new data are above the threshold within the new data
            any_onset_detected = np.any(onset_detected, axis=0)

            if any_onset_detected[0]:
                # convert timestamps to date time strings
                pretty_timestamps1 = [time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp)) for timestamp in onset_timestamps_1]
                print(f"onset detected for sensor 1 at {pretty_timestamps1}")
                threshold_publisher.send_string(f"emg_onset sensor1;{onset_timestamps_1}")
                if time.time() - last_vibrate_sensor_1 > vibrate_dely:
                    last_vibrate_sensor_1 = time.time()
                    vibrate_publisher.send_string(f"vibration vibrate_single")

            if any_onset_detected[1]:
                # convert timestamps to date time strings
                pretty_timestamps2 = [time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp)) for timestamp in onset_timestamps_2]
                print(f"onset detected for sensor 2 at {pretty_timestamps2}")
                threshold_publisher.send_string(f"emg_onset sensor2;{onset_timestamps_2}")
                if time.time() - last_vibrate_sensor_2 > vibrate_dely:
                    last_vibrate_sensor_2 = time.time()
                    vibrate_publisher.send_string(f"vibration vibrate_double")



if __name__ == "__main__":
    onset_detection()
