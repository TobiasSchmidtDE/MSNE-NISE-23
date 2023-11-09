# NISE Project - Team 1 - Infinite Runner Game 

## Module Overview
### Main Components:
- `arduino_controller`: A **Platform IO project** with the code that runs on the Arduino.
    - [x] Reads the data from the EMG sensors, computes the RMS and outputs it via a serial connection.
    - [ ] Defines a set of vibration patterns for the feedback motors and assigns commands to them.
    - [ ] Checks the serial connection for incoming commands and executes the corresponding vibration pattern.
- `serial_controller`: Python process managing the serial connection to the Arduino
    - [x] Establish and maintain a robust serial communication link.
    - [x] Encode and decode data to/from Arduino.
    - [x] Links to global zmq context to publish EMG data
    - [ ] Links to global zmq context subscribe to control commands to be forwarded.
    - [ ] Send control commands to Arduino to manage feedback motors.
    - [ ] Handle connection errors and automatic reconnection.
- `data_processor`: Python script for processing the EMG data
    - [ ] Links to global zmq context to subscribe to EMG data stream
    - [ ] Implement real-time EMG signal processing algorithms (e.g., feature extraction, gesture recognition).
    - [ ] Runs an adaptable threshold or machine learning model for gesture detection.
    - [ ] Optimize processing for minimal latency.
    - [ ] Publishes recognized gestures / movement to the `PyMessageHandler`.
    - [ ] Allow dynamic calibration for different users.
- `data_collector`: Python script for collecting the EMG data
    - [x] Links to global zmq context to subscribe to EMG data stream
    - [x] Store data in a structured and easily retrievable format (e.g., CSV, HDF5).
    - [ ] Implement data logging with time stamps, creating new files, etc..
    - [ ] Integrate a feature to label data for supervised learning purposes, possible some proper data collection paradigm.
- `game`: The infinite dino runner game based on PyGame
    - [ ] Develop game mechanics such as jumping, ducking, and obstacle generation.
    - [ ] Implement a scoring system based on survival time and obstacles passed.
    - [ ] Design game levels with increasing difficulty.
    - [ ] Links to `PyMessageHandler` via IPC to subscript to gesture recognition topic and interprets those as game controls.
    - [ ] Provide real-time feedback `PyMessageHandler` to be forwarded by PySerialController.
- `main`: Manages the multiprocess startup of all the modules

### Helper Modules:
- `serial_monitor`: Standalone Python script for monitoring the serial connection and plotting the data.
    - [x] Reads the data from the serial connection.
    - [x] Plots the data in real time.
    - [x] Buffers the data for simple processing.


## Python Setup

1. Have Conda installed. If you don't have it, install it from [here](https://docs.conda.io/en/latest/miniconda.html)
2. Create a new conda environment with `conda create -n nise python=3.9`.
3. Activate the environment with `conda activate nise`.
4. Install all python dependencies by running `pip install -r requirements.txt` in the root directory of this repository.
5. Install our emg_game pip package by running `pip install -e .` in the root directory of this repository.

To run the game, simple execute the `main.py` script in the root directory of this repository.



## Arduino Development Setup
To make the develeopment process significantly easier and more streamlined we are using the [PlatformIO](https://platformio.org/) IDE.

This IDE is an extension for [Visual Studio Code](https://code.visualstudio.com/) and can be installed as such.
Hopefully you're already using VSCode, if not, you should be. It's the best IDE period.

Since now you have VSCode installed, you can install the PlatformIO extension really easily. Just open the extensions tab on the left side of the screen and search for PlatformIO.

After cloning this repository you can open the project folder in VSCode and you should be good to go.
Since you have install the extension everything should update itself automatically and PlatformIO should install all the necessary dependencies and libraries automatically.
Altough this will take some time, so be patient.

Note: you should see a bunch of new symbols in the lower left corner of your VSCode window. If you don't see them, you probably have to restart VSCode for the extension to work properly.

## Arduino Development Workflow

- Edit code in the `src` folder; `main.cpp` is the program's entry point.
- Upload code to the Arduino with the arrow symbol in the bottom left corner of VSCode.
- Use the cable-symbol next to the arrow to open the serial monitor for program output.
- Remember: Close the serial monitor to upload new code, as the serial connection is exclusive to one program at a time.
