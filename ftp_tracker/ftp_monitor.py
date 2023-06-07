import os.path
import pathlib
import time
from ftplib import FTP, error_perm
import datetime
from threading import Thread

from process_fire.base.log import Log, error_wraps


class SettingClient:
    def __init__(self,
        host: str,
        login: str,
        password: str,
    ):
        self.host = host
        self.login = login
        self.password = password


class ManageFile:
    def __init__(
        self,
        output_dir: str = '.',
        path_to_filenames: str = 'filenames.txt'
    ):
        self.output_dir = output_dir
        self.path_to_filenames = path_to_filenames
        self.make_dir(output_dir)

    @classmethod
    def make_dir(cls, dirname) -> None:
        pathlib.Path(dirname).mkdir(parents=True, exist_ok=True)

    @classmethod
    def write_filenames_to_file(cls, filenames: list = None, path: str = 'data/filenames.txt', mode='a'):
        with open(path, mode) as file:
            if filenames:
                data = "".join(item + '\n' for item in filenames)
                file.write(data)

    def read_filenames_from_file(self, path: str = 'data/filenames.txt', callback=None):
        with open(path, 'r') as file:
            callback(
                set(self.to_list(file.read()))
            )


class FtpTracker(SettingClient, ManageFile):
    __date_format = '%m-%d-%y'
    __path_to_filenames_cur_day = 'data/filenames_cur_day.txt'
    __expansion_list = ('dbf', 'shx', 'prj', 'shp')

    def __init__(
        self,
        tracker_remote_dir: str = 'fire',
        **kwargs
    ):
        # self.logger = Log('log_ftp_monitor')
        ManageFile.__init__(
            self,
            kwargs.get('output_dir'),
            kwargs.get('path_to_filenames'),
        )
        SettingClient.__init__(
            self,
            kwargs.get('host'),
            kwargs.get('login'),
            kwargs.get('password'),
        )
        while True:
            try:
                self.ftp = FTP(self.host)
                print(2424)
                break
            except TimeoutError:
                print(1212)
                continue

        self.ftp.login(self.login, self.password)
        self.ftp.cwd(tracker_remote_dir)
        self.tracker_dir = tracker_remote_dir
        # self.output_dir = output_dir
        # self.path_to_filenames = path_to_filenames
        self.make_dir('data')
        self.logger = Log('logs')

    def __call__(self, *args, **kwargs):
        thread = Thread(target=self.__track_files_before_current_day(), daemon=False)
        thread.start()

    @error_wraps
    def to_list(self, filenames):
        return [filename for filename in filenames.split('\n')]

    @error_wraps
    def track_dir(self, remote_dir: str = '.'):
        ls_prev = set()
        try:
            self.read_filenames_from_file(self.__path_to_filenames_cur_day, ls_prev.update)
        except FileNotFoundError:
            self.write_filenames_to_file([], self.__path_to_filenames_cur_day, mode='w')

        ls = set()
        date = datetime.datetime.now().strftime(self.__date_format)

        while True:
            date_now = datetime.datetime.now().strftime(self.__date_format)

            if date < date_now:
                self.write_filenames_to_file(ls_prev, self.path_to_filenames)
                self.write_filenames_to_file([], self.__path_to_filenames_cur_day, mode='w')
                ls_prev = set()
                date = date_now

            if remote_dir == '.':
                for files_dir in self.ftp.nlst(remote_dir):
                    self._fetch_files_from_ftp(files_dir, ls.update)
            else:
                ls.clear()
                self._fetch_files_from_ftp(remote_dir, ls.update)

            add = ls-ls_prev

            if add:
                print(add)
                # self.write_filenames_to_file(add, self.__path_to_filenames_cur_day)
                yield add
            ls_prev = ls

            time.sleep(2)

    @error_wraps
    def download_file_retrbinary(self, file: str, to: str):
        return self.ftp.retrbinary('RETR ' + file, open(to, 'wb').write)

    @error_wraps
    def __track_files_before_current_day(self):
        filenames = set()
        try:
            self.read_filenames_from_file(self.path_to_filenames, filenames.update)
        except FileNotFoundError:
            self.write_filenames_to_file([], self.path_to_filenames, mode='w')

        download_files = set()
        for files_dir in self.ftp.nlst('.'):
            self._fetch_files_from_ftp(
                files_dir,
                download_files.update,
                datetime.datetime.now().strftime(self.__date_format)
            )

        files = download_files-filenames

        if not files:
            # print('not file')
            return

        # print(__name__)
        self.download_file_list(files)
        self.write_filenames_to_file(files)

    @error_wraps
    def download_file_list(self, files: list):
        added_files = []
        for file in files:
            print(file)
            # self.logger.logger.info('File %s written' % file)
            for expansion in self.__expansion_list:
                self.download_file_retrbinary(
                    f'{self.ftp.pwd()}/{file}.{expansion}',
                    f'{self.output_dir}/{os.path.basename(file)}.{expansion}'
                )
            added_files.append(file)
        return added_files

    @error_wraps
    def track_files_current_day(self):
        for files in self.track_dir('.'):
            added_files = self.download_file_list(
                list(files)
            )
            self.write_filenames_to_file(added_files, self.__path_to_filenames_cur_day)

    def run(self):
        self.track_files_current_day()

    @error_wraps
    def _fetch_files_from_ftp(self, remote_dir, callback=None, date_before=None):
        file_names = []

        remote_files = []
        self.ftp.retrlines(f'LIST {remote_dir}/*.shp', remote_files.append)

        for file_item in remote_files[:100]:
            file_metadata = list(
                filter(
                    lambda item: item != '',
                    file_item.split(' ')
                )
            )

            filename = file_metadata[3].split(".")[0]
            # print(file_item)
            if date_before:
                formatted_date = datetime.datetime.strptime(date_before, self.__date_format).strftime(self.__date_format)

                if file_metadata[0] < formatted_date:
                    file_names.append(f'{remote_dir}/{filename}')
            else:
                date_now = datetime.datetime.now().strftime(self.__date_format)
                if file_metadata[0] == date_now:
                    # print(date_now, filename)
                    # print(file_metadata)
                    file_names.append(f'{remote_dir}/{filename}')

        if not callback:
            return set(file_names)

        callback(
            set(file_names)
        )
