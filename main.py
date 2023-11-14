from multiprocessing import Process
from emg_game.serial_controller import run_serial_controller
from emg_game.data_collector import run_data_collector
from emg_game.data_monitor import run_data_monitor


def start_components():
    # Create processes for each component
    serial_process = Process(target=run_serial_controller)
    data_monitor_process = Process(target=run_data_monitor)
    data_collector_process = Process(target=run_data_collector)

    # Set the process as daemonic
    serial_process.daemon = True
    data_monitor_process.daemon = True
    data_collector_process.daemon = True

    # Start processes
    serial_process.start()
    data_monitor_process.start()
    data_collector_process.start()

    # Wait for processes to complete
    serial_process.join()
    data_monitor_process.join()
    data_collector_process.join()


if __name__ == "__main__":
    start_components()