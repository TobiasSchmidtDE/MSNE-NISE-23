from multiprocessing import Process
from emg_game.serial_controller import run_serial_controller
from emg_game.serial_controller_mocked import run_mock_serial_controller
from emg_game.data_collector import run_data_collector, run_labeled_data_collector
from emg_game.data_monitor import run_data_monitor
from emg_game.data_labeler import run_data_labeler
from pathlib import Path


def start_components(mode: str):
    processes = []
    # Create processes for each component
    # serial_process = Process(target=run_serial_controller)
    # data_collector_process = Process(target=run_data_collector)
    # data_monitor_process = Process(target=run_data_monitor)
    # data_labeler_process = Process(target=run_data_labeler)
    # data_label_collection_process = Process(target=run_labeled_data_collector)

    if mode == "labeled_data_collection":
        processes += [
            Process(target=run_serial_controller),
            Process(target=run_data_collector),
            Process(target=run_data_monitor),
            Process(target=run_data_labeler),
            Process(target=run_labeled_data_collector),
        ]
    elif mode == "data_collection":
        processes += [
            Process(target=run_serial_controller),
            Process(target=run_data_collector),
            Process(target=run_data_monitor),
        ]
    elif mode == "mock_controller":
        processes += [
            Process(
                target=run_mock_serial_controller,
                kwargs=dict(recording=str(Path("data/recordings/2023-11-15_21-15-09.csv"))),
            ),
            Process(
                target=run_data_collector,
                kwargs=dict(output_folder=str(Path("./data/recordings_mocked/"))),
            ),
            Process(target=run_data_monitor),
        ]

    # Set the process as daemonic
    for p in processes:
        p.daemon = True

    # Start processes
    for p in processes:
        p.start()

    # Wait for processes to complete
    for p in processes:
        p.join()


if __name__ == "__main__":
    start_components(mode="mock_controller")
