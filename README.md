# NISE Project - Team 1 - Infinite Runner Game 

## Module Overview

### EMG Controller
`serial_controller.py`: This module serves as the primary interface for serial communication with external hardware (e.g., Arduino). It uses the serial and zmq libraries for serial communication and inter-process communication (IPC), respectively. The module initializes a serial port for data transmission and sets up ZMQ PUB/SUB sockets for data publishing and command receiving. It continuously reads data from the serial port, timestamps it, and publishes it to a designated topic. Additionally, it listens for vibration commands from other modules and transmits these commands to the Arduino. This module is a crucial component in the data acquisition and control flow of the system.

`serial_controller_mocked.py`: This module acts as a mock version of the serial_controller.py, simulating serial data input for testing purposes. It reads a CSV file containing pre-recorded sensor data and publishes the data over a ZMQ socket at a specified rate. This module is essential for testing and validation of the system when actual hardware is not available or when reproducible data input is required.

`data_monitor.py`: The data_monitor.py module is responsible for real-time visualization of sensor data. It subscribes to the sensor data topic, processes incoming data, and displays it using Matplotlib's animation functionality. This module highlights temporal trends in sensor data, including mean and standard deviation calculations, making it a vital tool for monitoring and analyzing sensor output in real time.

`data_processor.py`: This module is key for data analysis and event detection. It subscribes to the sensor data topic, applies a moving average and standard deviation filter, and detects significant deviations in sensor readings (onsets). Detected onsets are published on a separate topic for downstream processing or triggering of events. The module's ability to detect meaningful changes in sensor data in real time is critical for responsive system behavior.

`data_collector.py`: This module is designed for data logging. It subscribes to sensor data and/or label data topics and writes the incoming data to CSV files for subsequent analysis or training machine learning models. The module supports both unlabeled and labeled data collection, making it versatile for various data gathering scenarios. It plays a key role in building a dataset for system performance evaluation and model training.

### Game
`chromedino.py`: This module is a recreation of the popular Chrome Dino game, enhanced with sensor-based control for jumping and ducking actions. It uses the pygame library for game development and zmq for inter-process communication. The game features a dinosaur character that the player controls to avoid obstacles by jumping or ducking. The character's actions can be controlled either by keyboard inputs or sensor signals received through a ZMQ subscription.

The game's architecture is modular, with classes representing the Dinosaur (player character), Clouds, and various Obstacles (Small Cactus, Large Cactus, Bird). These classes handle the individual behaviors and rendering of each game element. The main game loop in main() updates these elements, checks for collisions, and handles scoring and game speed.

Unique to this version is the integration of ZMQ to receive external sensor commands. The game subscribes to a ZMQ topic to receive "emg_onset" signals, which are used to trigger the dinosaur's jump or duck actions based on predefined sensor mappings (jump_sensor and duck_sensor). This feature allows for a more interactive and possibly accessible gameplay experience, as it can be controlled through external devices like EMG sensors.

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


## Running the EMG Controlled Game

1. Connect the Arduino to the computer via USB and figure out which Port is used (e.g. COM6).
2. Update the `SERIAL_PORT` varaible in `serial_controller.py` to the correct port.
3. Run `python emg_game/serial_controller.py` to start the serial controller.
4. Run `python emg_game/data_monitor.py` to start the data monitor. You should see a plot of the incoming data.
5. Run `python emg_game/data_processor.py` to start the data processor. **IMPORTANT**: In the very beginning there is a short calibration phase in which we calculate the standard deviation of the incoming data. The calculated value is going to stay fixed/constant for the rest of the program. Make sure to record a clean signal during this phase and don't move your arms/hands.
6. Run `cd dino_runner & python chromedino.py` to start the game. You should see the game window pop up.

How to play the game:
There are two ways of controlling the game. Either with the keyboard or with the EMG sensors.
Both work at the same time but it is highly recommended to turn the emg controller code off (at minimum the data_processor) when playing with the keyboard.

Keyboard controls:
- Press space or arrow up to jump
- Press down arrow to duck

EMG controls:
By default sensor 1 is mapped to jump and sensor 2 is mapped to duck.
When you clench your fist of either hand (1 or 2) the dinosaur will jump or duck.

In the main menu you can control which sensor to use for jumping and ducking.
It's very simple: What ever fist you clench will start the game and be used for jumping commands. The other fist will be used for ducking commands.