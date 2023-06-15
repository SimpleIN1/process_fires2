
import glob
import os

import fnmatch
import pathlib
from threading import Thread

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from process_fire.base.database import DataBase
from process_fire.base.log import Log, error_wraps
from process_fire.files_tracker.shp import ShapeFile


class FileHandler(FileSystemEventHandler):
    db = DataBase()

    #def __check_files(self, path):
    #    dirname = os.path.dirname(path)
    #    filename = os.path.basename(path).split('.')[0]
    #    print(os.path.exists(f'{dirname}/{filename}.dbf'))
    #    print(os.path.exists(f'{dirname}/{filename}.shx'))
    #    print(os.path.exists(f'{dirname}/{filename}.prj'))
    #    print(os.path.exists(f'{dirname}/{filename}.shp'))

    #def on_created(self, event):
    #    path = event.src_path
    #    # self.__check_files(path)
    #    if fnmatch.fnmatch(path, '*.shp'):
    #        print('File write increated %s' % path)
    #        # self.__check_files(path)
    #        FileTracker.add_fire_values(path, self.db)


    __not_loading_files = []

    def __check_files(self, path):
        dirname = os.path.dirname(path)
        filename = os.path.basename(path).split('.')[0]
        for expansion in ('dbf', 'prj', 'shx', 'shp'):
            if not os.path.exists(f'{dirname}/{filename}.{expansion}'):
                return False
        return True

    def __write_not_inserted_file(self):    
        if len(self.__not_loading_files) != 0:
            print('Unsuccessfully -', self.__not_loading_files)
            for index, file in enumerate(self.__not_loading_files):
                if self.__check_files(file):
                    FileTracker.add_fire_values(file, self.db)
                    self.__not_loading_files.pop(index)

    def on_created(self, event):
        path = event.src_path
        if fnmatch.fnmatch(path, '*.shp'):
            print('File write increated %s' % path)

            self.__write_not_inserted_file()

            if self.__check_files(path):
                #print(path, 'successfully')
                FileTracker.add_fire_values(path, self.db)
            else:
                print('--', path)
                self.__not_loading_files.append(path)


    def on_moved(self, event):
        print('Onmoved')


class FileTracker:
    db = DataBase()

    def __init__(self, path_to_files):
        # self.logger = Log('logs_tracker_files')
        self.path_to_files_for_track = path_to_files
        self.make_dir(path_to_files)
        # self.logger = Log('logs')

    def make_dir(self, dirname) -> None:
        pathlib.Path(dirname).mkdir(parents=True, exist_ok=True)

    @error_wraps
    def run_tracker(self) -> None:
        print('Tracker run')
        event_handler = FileHandler()
        observer = Observer()
        observer.schedule(event_handler, path=self.path_to_files_for_track, recursive=True)
        observer.start()

        while True:
            pass

    def run(self):
        self.db.create_tables()

        thread = Thread(target=self.read_files(), daemon=False, name='Thread1')
        thread.start()
        print(thread.getName)

        self.run_tracker()

    @classmethod
    @error_wraps
    def add_fire_values(cls, path, db):
        shp = ShapeFile(path)
        alg_name, satellite, date_time, round_frame = shp.parse_filename()
        # print(shp.parse_filename())
        data_fires = shp.read_shape_file()
        #print(data_fires)
        if data_fires:
            db.insert_data_fires(
                date_time=date_time,
                data_fires=data_fires,
                alg_name=alg_name,
                satellite=satellite,
                round=round_frame
            )

            dirname = os.path.dirname(path)
            filename = os.path.basename(path).split('.')[0]
            for expansion in ('dbf', 'prj', 'shx', 'shp'):
                os.remove(f'{dirname}/{filename}.{expansion}')

    @error_wraps
    def read_files(self):
        for file in glob.glob(f'{self.path_to_files_for_track}/*.shp'):
            self.add_fire_values(file, self.db)




