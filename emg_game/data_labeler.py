import zmq
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.patches as patches
import numpy as np
import random
import time
import matplotlib

# Get the current backend
current_backend = matplotlib.get_backend()
print("Current Matplotlib backend:", current_backend)

# Constants
FIG_SIZE = (12, 8)  # Figure size (width, height) in inches
ANIMATION_INTERVAL = 5  # Animation update interval in milliseconds
SIMULATION_TIME = 60  # Total simulation time in seconds (10 minutes)
SAMPLE_RATE = 100  # Sample rate in Hz
MAX_SIZE = (
    SAMPLE_RATE * SIMULATION_TIME
)  # Max size of the data array / axis length, 30 seconds at 60Hz
SPIKE_DURATION = int(0.5 * SAMPLE_RATE)  # Duration of each spike in samples
WINDOW_SIZE = SAMPLE_RATE * 10
NUMBER_OF_SPIKES = 25  # Total number of spikes to generate

# Constants for new spike generation
CALIBRATION_TIME = 10  # Calibration/warm-up time in seconds
CALIBRATION_SAMPLES = CALIBRATION_TIME * SAMPLE_RATE  # Calibration samples


# Function to generate spikes with calibration period
def generate_spikes_with_calibration(spike_value_left=3, spike_value_right=8):
    # Generate uniformly distributed random spike times after calibration period
    # An actual uniform distribution makes it way to likely to have spikes too close to each other
    # Therefore we generate a linspace and add some random noise
    spike_times = np.linspace(
        CALIBRATION_SAMPLES,
        MAX_SIZE - WINDOW_SIZE - SPIKE_DURATION,
        NUMBER_OF_SPIKES,
        dtype=int,
    )
    # calculate the mean interval between spikes
    mean_interval = (
        MAX_SIZE - WINDOW_SIZE - SPIKE_DURATION - CALIBRATION_SAMPLES
    ) / NUMBER_OF_SPIKES
    spike_times += np.random.randint(
        int(-mean_interval * 0.5), int(mean_interval * 0.5), NUMBER_OF_SPIKES
    )

    # Initialize traces
    left_trace = np.zeros(MAX_SIZE)
    right_trace = np.zeros(MAX_SIZE)

    # the first spike is always on the right
    right_trace[spike_times[0] : spike_times[0] + SPIKE_DURATION] = spike_value_right

    # Assign spikes to left or right and update traces
    for spike_time in spike_times[1:]:
        if random.choice([True, False]):  # Randomly choose left or right
            left_trace[spike_time : spike_time + SPIKE_DURATION] = spike_value_left
        else:
            right_trace[spike_time : spike_time + SPIKE_DURATION] = spike_value_right

    return left_trace, right_trace


# Generate spikes for left and right traces with calibration period
left_trace, right_trace = generate_spikes_with_calibration()


def run_data_labeler():
    context = zmq.Context()
    publisher = context.socket(zmq.PUB)
    publisher.bind(f"tcp://*:{5557}")

    create_label_plot(publisher, left_trace, right_trace)


def create_label_plot(publisher, left_trace, right_trace):
    fig, (ax1, ax2) = plt.subplots(
        2, 1, figsize=FIG_SIZE, gridspec_kw={"height_ratios": [1, 2]}
    )
    xs_window = np.arange(0, WINDOW_SIZE)
    xs_full = np.arange(0, MAX_SIZE)
    start_time = time.time()
    # Plot for the full trace
    # Create a gray rectangle overlay for the ax1 plot
    rect = patches.Rectangle(
        (0, 0),
        WINDOW_SIZE,
        10,
        linewidth=1,
        edgecolor="none",
        facecolor="gray",
        alpha=0.5,
    )
    ax1.add_patch(rect)

    ax1.plot(xs_full, left_trace, label="Left Hand", color="blue")
    ax1.plot(xs_full, right_trace, label="Right Hand", color="orange")
    ax1.set_title("Overview")
    # ax1.set_xlabel("Sample Number")
    ax1.set_ylabel("Signal Value")
    ax1.legend(loc="upper left")

    # Vertical line for the animated plot
    action_line_pos = WINDOW_SIZE // 2
    action_line_1 = ax1.axvline(x=action_line_pos, color="red", linestyle="--")
    action_line_2 = ax2.axvline(x=action_line_pos, color="red", linestyle="--")

    def animate(i, left_trace, right_trace):
        current_time = time.time()
        elapsed_time = current_time - start_time
        sample_index = int(elapsed_time * SAMPLE_RATE) % (MAX_SIZE - WINDOW_SIZE)
        end_index = sample_index + WINDOW_SIZE

        # Slicing the traces for the current window
        current_left_trace = left_trace[sample_index:end_index]
        current_right_trace = right_trace[sample_index:end_index]

        # Update the position of the gray rectangle on ax1
        rect.set_x(sample_index)
        rect.set_width(WINDOW_SIZE)
        action_line_1.set_xdata(sample_index + action_line_pos)

        # Update the animated plot
        ax2.clear()
        ax2.set_xlim(0, WINDOW_SIZE - 1)
        ax2.set_ylim(0, 10)
        ax2.plot(xs_window, current_left_trace, label="Left Hand", color="blue")
        ax2.plot(xs_window, current_right_trace, label="Right Hand", color="orange")
        ax2.fill_between(
            xs_window,
            np.zeros_like(current_left_trace),
            current_left_trace,
            color="blue",
            alpha=0.5,
        )
        ax2.fill_between(
            xs_window,
            np.zeros_like(current_right_trace),
            current_right_trace,
            color="orange",
            alpha=0.5,
        )
        ax2.axvline(x=WINDOW_SIZE // 2, color="red", linestyle="--")

        ax2.set_title("Real-time Window")
        ax2.set_xlabel("Sample Number")
        ax2.set_ylabel("Signal Value")
        ax2.legend(loc="upper left")

        # Publish the label data on the "label_data" topic
        # the format should be timestamp, left_label, right_label
        decoded_bytes = f"{time.time()},{left_trace[sample_index + action_line_pos]},{right_trace[sample_index + action_line_pos]}"
        publisher.send_string(f"label_data {decoded_bytes}")

    ani = animation.FuncAnimation(
        fig,
        animate,
        fargs=(
            left_trace,
            right_trace,
        ),
        interval=ANIMATION_INTERVAL,
    )

    # to put it into the upper left corner for example:
    # mngr = plt.get_current_fig_manager()
    # mngr.window.setGeometry(443, -1049, 1916, 564)

    plt.show()
    # send message to start labeled data collection
    # publisher.send_string(f"label_data start")


if __name__ == "__main__":
    run_data_labeler()
