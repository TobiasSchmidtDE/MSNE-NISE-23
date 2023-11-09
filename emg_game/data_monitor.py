import zmq
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np


def run_data_monitor(port=5556, topic="emg_data"):
    context = zmq.Context()
    subscriber = context.socket(zmq.SUB)
    subscriber.connect(f"tcp://localhost:{port}")
    subscriber.setsockopt_string(zmq.SUBSCRIBE, topic)

    create_data_monitor_plot(subscriber)


def create_data_monitor_plot(subscriber):
    # Customizable constants
    FIG_SIZE = (12, 6)  # Figure size (width, height) in inches
    MAX_SIZE = 500  # Max size of the data array / axis length
    ANIMATION_INTERVAL = 1  # Animation update interval in milliseconds
    BUFFER_SIZE = MAX_SIZE * 10  # Size of the data buffer for background processing

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
    def animate(
        i, ys1, ys2, data_buffer1, data_buffer2, rolling_stats1, rolling_stats2
    ):
        # Process all available messages
        i = 0
        while True:
            try:
                i += 1
                topic, message = subscriber.recv_string(flags=zmq.NOBLOCK).split()
                # Split the string into the two sensor values
                sensor_1, sensor_2 = message.split(",")
                # Convert the sensor values to floats and add to buffer
                sensor_value_1 = float(sensor_1)
                sensor_value_2 = float(sensor_2)

                # Update the buffers with new sensor values
                data_buffer1[:] = np.roll(data_buffer1, -1)
                data_buffer2[:] = np.roll(data_buffer2, -1)
                data_buffer1[-1] = sensor_value_1
                data_buffer2[-1] = sensor_value_2

                stats_window1 = data_buffer1[-50:]
                stats_window2 = data_buffer2[-50:]
                # Fill up the ys arrays with data until they're full, then start rolling
                if np.isnan(ys1).any():
                    ys1[np.isnan(ys1).argmax()] = sensor_value_1
                    ys2[np.isnan(ys2).argmax()] = sensor_value_2

                    # Calculate mean and standard deviation for visible data
                    rolling_stats1["mean"][
                        np.isnan(rolling_stats1["mean"]).argmax()
                    ] = np.nanmean(stats_window1, axis=0)
                    rolling_stats1["std"][
                        np.isnan(rolling_stats1["std"]).argmax()
                    ] = np.nanstd(stats_window1, axis=0)
                    rolling_stats2["mean"][
                        np.isnan(rolling_stats2["mean"]).argmax()
                    ] = np.nanmean(stats_window2, axis=0)
                    rolling_stats2["std"][
                        np.isnan(rolling_stats2["std"]).argmax()
                    ] = np.nanstd(stats_window2, axis=0)
                else:
                    ys1[:] = np.roll(ys1, -1)
                    ys2[:] = np.roll(ys2, -1)
                    ys1[-1] = sensor_value_1
                    ys2[-1] = sensor_value_2

                    # Calculate mean and standard deviation for visible data
                    rolling_stats1["mean"][:] = np.roll(rolling_stats1["mean"], -1)
                    rolling_stats1["mean"][-1] = np.nanmean(stats_window1, axis=0)
                    rolling_stats1["std"][:] = np.roll(rolling_stats1["std"], -1)
                    rolling_stats1["std"][-1] = np.nanstd(stats_window1, axis=0)
                    rolling_stats2["mean"][:] = np.roll(rolling_stats2["mean"], -1)
                    rolling_stats2["mean"][-1] = np.nanmean(stats_window2, axis=0)
                    rolling_stats2["std"][:] = np.roll(rolling_stats2["std"], -1)
                    rolling_stats2["std"][-1] = np.nanstd(stats_window2, axis=0)

            except zmq.Again:
                # No more messages in the queue, break the loop to update the plot
                break

        print(f"Processed {i} messages")

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
            alpha=0.25,
        )

        # Draw mean and standard deviation for Sensor 2
        ax.plot(xs, rolling_stats2["mean"], label="Sensor 2 Mean", color="red")
        ax.fill_between(
            xs,
            rolling_stats2["mean"] + rolling_stats2["std"],
            rolling_stats2["mean"] - rolling_stats2["std"],
            color="orange",
            alpha=0.25,
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


if __name__ == "__main__":
    run_data_monitor()
