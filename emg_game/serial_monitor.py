import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import serial

# Customizable constants
SERIAL_PORT = "COM9"  # Serial port
BAUD_RATE = 512000  # Baud rate for serial communication
FIG_SIZE = (12, 6)  # Figure size (width, height) in inches
MAX_SIZE = 500  # Max size of the data array / axis length
ANIMATION_INTERVAL = 10  # Animation update interval in milliseconds
BUFFER_SIZE = MAX_SIZE * 10  # Size of the data buffer for background processing

# Initialize serial port
ser = serial.Serial(SERIAL_PORT, BAUD_RATE)
ser.flushInput()

# Create figure for plotting with a specified size
fig, ax = plt.subplots(figsize=FIG_SIZE)
ax.set_xlim(0, MAX_SIZE - 1)
xs = np.arange(0, MAX_SIZE)  # x-axis is simply a range of sample numbers
ys1 = np.full(MAX_SIZE, np.nan)
ys2 = np.full(MAX_SIZE, np.nan)
data_buffer1 = np.full(BUFFER_SIZE, np.nan)
data_buffer2 = np.full(BUFFER_SIZE, np.nan)
rolling_stats1 = {
    "mean": np.full(MAX_SIZE, np.nan),
    "std": np.full(MAX_SIZE, np.nan),
}
rolling_stats2 = {
    "mean": np.full(MAX_SIZE, np.nan),
    "std": np.full(MAX_SIZE, np.nan),
}


# This function is called periodically from FuncAnimation
def animate(i, ys1, ys2, data_buffer1, data_buffer2, rolling_stats1, rolling_stats2):
    # Read a line (ending in \n) from the serial port
    ser_bytes = ser.readline()

    # Decode bytes to string
    decoded_bytes = ser_bytes[0 : len(ser_bytes) - 2].decode("utf-8")

    # Split the string into the two sensor values
    sensor_1, sensor_2 = decoded_bytes.split(",")

    # Convert the sensor values to floats and add to buffer
    sensor_value_1 = float(sensor_1)
    sensor_value_2 = float(sensor_2)

    # Update the buffers with new sensor values
    data_buffer1[:] = np.roll(data_buffer1, -1)
    data_buffer2[:] = np.roll(data_buffer2, -1)
    data_buffer1[-1] = sensor_value_1
    data_buffer2[-1] = sensor_value_2

    # Fill up the ys arrays with data until they're full, then start rolling
    if np.isnan(ys1).any():
        ys1[np.isnan(ys1).argmax()] = sensor_value_1
        ys2[np.isnan(ys2).argmax()] = sensor_value_2

        # Calculate mean and standard deviation for visible data
        rolling_stats1["mean"][np.isnan(rolling_stats1["mean"]).argmax()] = np.nanmean(
            data_buffer1, axis=0
        )
        rolling_stats1["std"][np.isnan(rolling_stats1["std"]).argmax()] = np.nanstd(
            data_buffer1, axis=0
        )
        rolling_stats2["mean"][np.isnan(rolling_stats2["mean"]).argmax()] = np.nanmean(
            data_buffer2, axis=0
        )
        rolling_stats2["std"][np.isnan(rolling_stats2["std"]).argmax()] = np.nanstd(
            data_buffer2, axis=0
        )
    else:
        ys1[:] = np.roll(ys1, -1)
        ys2[:] = np.roll(ys2, -1)
        ys1[-1] = sensor_value_1
        ys2[-1] = sensor_value_2

        # Calculate mean and standard deviation for visible data
        rolling_stats1["mean"][:] = np.roll(rolling_stats1["mean"], -1)
        rolling_stats1["mean"][-1] = np.nanmean(data_buffer1, axis=0)
        rolling_stats1["std"][:] = np.roll(rolling_stats1["std"], -1)
        rolling_stats1["std"][-1] = np.nanstd(data_buffer1, axis=0)
        rolling_stats2["mean"][:] = np.roll(rolling_stats2["mean"], -1)
        rolling_stats2["mean"][-1] = np.nanmean(data_buffer2, axis=0)
        rolling_stats2["std"][:] = np.roll(rolling_stats2["std"], -1)
        rolling_stats2["std"][-1] = np.nanstd(data_buffer2, axis=0)

    # Draw x and y lists
    ax.clear()
    ax.set_xlim(0, MAX_SIZE - 1)
    ax.plot(xs, ys1, label="Sensor 1")
    ax.plot(xs, ys2, label="Sensor 2")

    # Draw mean and standard deviation
    ax.plot(xs, rolling_stats1["mean"], label="Sensor 1 Mean", color="blue")
    ax.fill_between(
        xs,
        rolling_stats1["mean"] + rolling_stats1["std"],
        rolling_stats1["mean"] - rolling_stats1["std"],
        color="lightblue",
        alpha=0.5,
    )

    # Draw mean and standard deviation for Sensor 2
    ax.plot(xs, rolling_stats2["mean"], label="Sensor 2 Mean", color="red")
    ax.fill_between(
        xs,
        rolling_stats2["mean"] + rolling_stats2["std"],
        rolling_stats2["mean"] - rolling_stats2["std"],
        color="orange",
        alpha=0.5,
    )

    # Format plot
    plt.title("EMG Sensor Data over Time")
    plt.ylabel("Sensor Value")
    plt.xlabel("Sample Number")
    plt.legend(loc="upper left")


# Set up plot to call animate() function periodically
ani = animation.FuncAnimation(
    fig,
    animate,
    fargs=(ys1, ys2, data_buffer1, data_buffer2, rolling_stats1, rolling_stats2),
    interval=ANIMATION_INTERVAL,
)
plt.show()
