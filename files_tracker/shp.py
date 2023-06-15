import time
from datetime import datetime

import fiona
import os
import shapefile
import geopandas as gpd
from process_fire.base.log import error_wraps


class ShapeFile:
    def __init__(self, filename):
        self.filename = filename

    @error_wraps
    def read_shape_file(self):

        # filename = os.path.basename(self.filename).split('.')[0]
        # dirname = os.path.dirname(self.filename)

        # data = fiona.open(self.filename)
        # print(self.filename)
        # print(data.schema)a
        #print(f'===={dirname}/{filename}.shp')
        # data = shapefile.Reader(
        #     shx=f'{dirname}/{filename}.shx',
        #     dbf=f'{dirname}/{filename}.dbf',
        #     shp=f'{dirname}/{filename}.shp',
        # )
        #for item in data:
        #    print(item.record)
        #print(data)

        count = 0
        while count < 3:
            try:
                data = gpd.read_file(self.filename)
                if count > 1:
                    print('Second circle gpd -> ' + self.filename)
                else:
                    print('gpd -> ' + self.filename)
                break
            except:
                print('error read ' + self.filename)
            count += 1

        if count > 2:
            raise Exception('File is not read')

        return data

    @classmethod
    @error_wraps
    def cut_expansion(cls, filename):
        return filename.split('.')[0]

    @error_wraps
    def parse_filename(self):
        tmp = os.path.basename(self.cut_expansion(self.filename)).split("_")

        return (
            tmp[0],
            tmp[1],
            datetime.strptime(tmp[2]+tmp[3]+tmp[4], "%Y%m%d%H%M"),
            tmp[6]
        )
