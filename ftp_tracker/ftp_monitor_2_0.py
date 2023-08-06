import datetime
import os.path
import pathlib
import time
from ftplib import FTP



class SettingUser:
    def __init__(self,
        host: str,
        login: str,
        password: str,
    ):
        self.host = host
        self.login = login
        self.password = password


class File:

    def __init__(self, dir):
        # self.path = path if path else self.default_path
        self.dir = dir
        self.make_dir(dir)

    @classmethod
    def make_dir(cls, dir: str) -> None:
        pathlib.Path(dir).mkdir(parents=True, exist_ok=True)

    @classmethod
    def write_to_file(
        cls,
        path: str,
        file_list: list = None,
        mode='a'
    ):
        with open(path, mode) as file:
            if file_list:
                data = "".join(item + '\n' for item in file_list)
                file.write(data)

    @classmethod
    def to_list(cls, file_list):
        return [item for item in file_list.split('\n')]

    @classmethod
    def read_from_file(cls, path: str, callback=None):
        with open(path, 'r') as file:
            callback(
                set(cls.to_list(file.read()))
            )


class TrackFTP(SettingUser, File):
    __expansion_list = ('dbf', 'shx', 'prj', 'shp')
    ftp = None

    def __init__(self,*args, **kwargs):
        File.__init__(
            self,
            kwargs.get('dir_data'),
        )
        SettingUser.__init__(
            self,
            kwargs.get('host'),
            kwargs.get('login'),
            kwargs.get('password'),
        )
        self.output_dir = kwargs.get('output_dir')
        self.connect()
        self.ftp.cwd(kwargs.get('tracker_remote_dir'))
        self.loaded_files = []

    def connect(self):
        connected = False

        while True:
            try:
                self.ftp = FTP(self.host, timeout=5)
                print('-> Connected')
            except:
                print('-> Reconnect')
                continue
            else:
                connected = True
                break

        if connected:
            self.ftp.login(self.login, self.password)

    def download_file(self, file: str, to: str):
        try:
            self.ftp.retrbinary('RETR ' + file, open(to, 'wb').write)
        except:
            return False
        else:
            return True

    def download_file_list(self, file_list):
        download_files = []
        self.loaded_files = []
        for file in file_list:
            filename = os.path.basename(file).split('.')[0]
            dir = os.path.dirname(file)
            for expansion in self.__expansion_list:
                if not self.download_file(
                    f'{self.ftp.pwd()}/{dir}/{filename}.{expansion}',
                    f'{self.output_dir}/{filename}.{expansion}',
                ):
                    break
            else:
                print(file)
                download_files.append(file)

        self.loaded_files.extend(download_files)

        return download_files

    def track(self, path_track: str = '.'):
        old_files = set()
        path_save = f'{self.dir}/filenames.txt'

        try:
            self.read_from_file(path_save, old_files.update)
        except FileNotFoundError:
            self.write_to_file(path_save, [], mode='w')

        while True:
            temp = set()

            for remote_dir in self.ftp.nlst(path_track):
                temp.update(self.ftp.nlst(f'{remote_dir}/*.shp'))

            new_files = temp - old_files
            if new_files:
                yield new_files

            not_loading_files = set(new_files) - set(self.loaded_files)

            if not_loading_files:
                print(f'First round, these files was loaded: {not_loading_files}')

                for filename in not_loading_files:
                    temp.remove(filename)

            old_files = temp
            time.sleep(8)

    @classmethod
    def check_format(cls, path: str) -> bool:
        filename = os.path.basename(path)
        name = filename.split('.')
        if len(name) != 2:
            return False

        tmp = name[0].split('_')
        if len(tmp) != 7:
            return False

        try:
            datetime.datetime.strptime(f'{tmp[2]}_{tmp[3]}_{tmp[4]}_{tmp[5]}', '%Y%m%d_%H_%M_%S')
        except ValueError:
            return False

        return True

    def check_format_list(self, file_list) -> list:
        validated_file_list = [filename for filename in file_list if self.check_format(filename)]
        return validated_file_list

    def get_data_tracker(self, dir_track):
        path_save = f'{self.dir}/filenames.txt'
        for files in self.track(dir_track):
            written_files = self.download_file_list(self.check_format_list(files))
            # print(sorted(written_files))
            # for item in sorted(written_files):
            #     print(item)
            self.write_to_file(
                path=path_save,
                file_list=list(written_files)
            )

    def get_downloading_files(self):
        temp = set()
        for remote_dir in self.ftp.nlst('.'):
            temp.update(self.ftp.nlst(f'{remote_dir}/*.shp'))

        path_save = f'{self.dir}/filenames.txt'

        file_list = []
        for file in temp:
            if self.check_format(file):
                tmp = os.path.basename(file).split('.')[0].split('_')
                # print(tmp)
                file_datetime = datetime.datetime.strptime(f'{tmp[2]}_{tmp[3]}_{tmp[4]}_{tmp[5]}', '%Y%m%d_%H_%M_%S').strftime('%Y%m%d_%H_%M_%S')
                # print(file_datetime)
                if file_datetime <= '20230610_08_50_25':
                    file_list.append(file)
                # else:
                #     print(file)

        self.write_to_file(path_save, file_list, mode='w')

    def run(self):
        self.get_data_tracker('.')

