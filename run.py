import config
#from . import config
from ftp_tracker.ftp_monitor_2_0 import TrackFTP


def main():
    ftp = TrackFTP(
        output_dir=config.monitor_dir,
        tracker_remote_dir='fire',
        host=config.ftp_server,
        login=config.ftp_login,
        password=config.ftp_password,
        dir_data='data',
    )
    ftp.get_downloading_files()
    #ftp.run()
    


if __name__ == '__main__':
    main()




