from datetime import datetime

import fiona
import os
import shapefile
from process_fire.base.log import error_wraps


class ShapeFile:
    def __init__(self, filename):
        self.filename = filename

    @error_wraps
    def read_shape_file(self):
        #data = fiona.open(self.filename)
        # print(data.schema)a
        filename = os.path.basename(self.filename).split('.')[0] 
        dirname = os.path.dirname(self.filename)
        #print(f'===={dirname}/{filename}.shp')
        data = shapefile.Reader(
            dbf=f'{dirname}/{filename}.dbf',
            shp=f'{dirname}/{filename}.shp',
        )
        #for item in data:
        #    print(item.record)
        #print(data)
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
