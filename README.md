# NISE Project - Team 1


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
From here on it's pretty straight forward. You can open the `src` folder and start editing the code. The `main.cpp` file is the entry point of the program and is the first file that gets executed when the Arduino is powered on. If you make any changes to it and want to push the code to the arduino, simply click on the arrow symbol in the lower left corner of your vscode window. This will compile the code and upload it to the Arduino. If you want to see the output of the program, you can open the serial monitor by clicking on the cable-symbol next to the arrow symbol. This will open a new window in VSCode where you can see the output of the program. 
Note: The serial connection can only be used by one program at a time. So if you have the serial monitor open, you can't upload new code to the Arduino. You have to close the serial monitor first. Same goes for using the serial plotter of the Arduino IDE. 


## Python Setup

1. Have Conda installed. If you don't have it, install it from [here](https://docs.conda.io/en/latest/miniconda.html)
2. Create a new conda environment with `conda create -n nise python=3.9`.
3. Activate the environment with `conda activate nise`.
4. Install the requirements with `pip install -r requirements.txt`
