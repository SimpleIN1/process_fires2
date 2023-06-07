from process_fire.ftp_tracker.ftp_monitor import FtpTracker
from process_fire import config


def main():
    ftp = FtpTracker(
        tracker_remote_dir='fire',
        output_dir=config.monitor_dir,
        path_to_filenames='data/filenames.txt',
        host=config.ftp_server,
        login=config.ftp_login,
        password=config.ftp_password,
    )
    ftp()
    ftp.run()


if __name__ == '__main__':
    main()




