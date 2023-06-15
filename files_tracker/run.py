from process_fire.config import monitor_dir
from process_fire.files_tracker.tracker_files import FileTracker


def main():
    ft = FileTracker(
        path_to_files=monitor_dir
    )
    ft.run()


if __name__ == '__main__':
    main()
