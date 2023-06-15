import glob
import json
import pprint
import os
import shapefile
from shapely import wkb
from shapely.geometry import shape, Point

from process_fire.base.database import DataBase


#ГовнA код

'''
[
    id: {
        polygon: ...,
        latitude: ...,
        longitude: ...,
        name: ...,
        population: ...,
        type_settlement: ...,
    }
]


Fetch the settlement polygon and point type of the object.
{
    'city_town': {
        
    },
    'village_hamlet': {
        
    }
}
'''

# path_settlement_point = '/home/grigoriy/Загрузки/new_z/Nas_punkt'
# path_settlement_polygon = '/home/grigoriy/Загрузки/new_z/Nas_punkt_polygon'


def fetch_settlement_point_list(path):
    settlement_list = []

    for file in glob.glob(path):
        filename = os.path.basename(file).split('.')[0]
        dirname = os.path.dirname(file)

        data = shapefile.Reader(
            shp=f'{dirname}/{filename}.shp',
            dbf=f'{dirname}/{filename}.dbf',
        )

        for row in data:
            if row.record['NAME'] is not None:
                settlement_list.append({
                    'name': row.record['NAME'],
                    'type': row.record['PLACE'],
                    'population': row.record['POPULATION'],
                    'point': shape(row.shape),
                    'poly': None
                })

    return settlement_list


def fetch_settlement_polygon(path):

    settlement_dict_point = {
        'city_town': [],
        'village_hamlet': [],
    }

    for file in glob.glob(path):
        filename = os.path.basename(file).split('.')[0]
        dirname = os.path.dirname(file)

        data = shapefile.Reader(
            shp=f'{dirname}/{filename}.shp',
            dbf=f'{dirname}/{filename}.dbf',
        )
        # print(f'{dirname}/{filename}.shp')
        for row in data:

            # if shape(row.shape).contains(Point(88.200517, 69.3498394)):
            #     print(row.record)
            if row.record['PLACE'] in ('city', 'town'):
                attribute = 'city_town'
            if row.record['PLACE'] in ('hamlet', 'village'):
                attribute = 'village_hamlet'

            settlement_dict_point[attribute].append({
                'name': row.record['NAME'],
                'type': row.record['PLACE'],
                'population': row.record['POPULATION'],
                'poly': shape(row.shape)
            })

    return settlement_dict_point


def make_list_settlements(path_settlement_polygon: str, path_settlement_point: str):
    settlement_polygon_dict = fetch_settlement_polygon(f'{path_settlement_polygon}/*/*.shp')
    settlement_list = fetch_settlement_point_list(f'{path_settlement_point}/*.shp')

    for index, settlement_point in enumerate(settlement_list):
        type = 'city_town' if settlement_point['type'] in 'city_town' else 'village_hamlet'
        for index_poly, settlement_polygon in enumerate(settlement_polygon_dict[
            type
        ]):
            if settlement_polygon['poly'].contains(settlement_point['point']):
                settlement_list[index]['poly'] = settlement_polygon['poly']

                if settlement_list[index]['type'] != settlement_polygon['type']:
                    settlement_list[index]['type'] = settlement_polygon['type']

                settlement_polygon_dict[type].pop(index_poly)
                break
        if 6000 < index <= 6001:
            print('THe half is performed')
    print('Formatted')
    return settlement_list


def make_by_type(path_settlement_polygon):
    count = {
        'village': 0,
        'town': 0,
        'hamlet': 0,
        'city': 0
    }
    count_data = 0

    for file in glob.glob(f'{path_settlement_polygon}/*/*.shp'):

        file_without_expansion = os.path.basename(file).split('.')[0]
        dirname = os.path.dirname(file)

        data = shapefile.Reader(
            shp=f'{dirname}/{file_without_expansion}.shp',
            dbf=f'{dirname}/{file_without_expansion}.dbf',
        )
        length = len(data)
        # print(dirname, length)
        count_data += length

        for row in data.iterRecords():
            if row['PLACE'] == 'village':
                # print(row)
                count['village'] += 1
            if row['PLACE'] == 'town':
                # print(row)
                count['town'] += 1
            if row['PLACE'] == 'city':
                # print(row)
                count['city'] += 1
            if row['PLACE'] == 'hamlet':
                # print(row)
                count['hamlet'] += 1

    # pprint.pprint(count)
    print('Count all', count_data)


def write_to_file(json_object, file_write):
    out_json = json.dumps(json_object)
    with open(file_write, mode='w', encoding='utf-8') as out_file:
        out_file.write(out_json)


def fetch_xy_from_poly(p):
    xy = p.exterior.xy
    return [
        [xy[1][i], xy[0][i]] for i in range(len(xy[0]))
    ]


def to_json():
    db = DataBase()
    settlements = db.get_settlements()
    settlements_json = {}

    for settlement in settlements:
        l = None

        if settlement.poly is not None:
            pl = wkb.loads(bytes(settlement.poly.data))
            if pl.type == 'MultiPolygon':
                l = [fetch_xy_from_poly(p) for p in pl.geoms]
            else:
                l = fetch_xy_from_poly(pl)

        point = wkb.loads(bytes(settlement.point.data))

        settlements_json[settlement.id] = {
            'name': settlement.name,
            'population': settlement.population,
            'type': settlement.type,
            'poly': l,
            'longitude': point.x,
            'latitude': point.y,
        }
        # pprint.pprint(settlements_json)
        # break

    write_to_file({
        'settlements': settlements_json,
    }, 'settlement_out_3.json')


def from_json(path):
    with open(path, mode='r', encoding='utf-8') as in_file:
        return json.load(in_file)
    # print(data)
    # in_file.close()
    # return data


def run():

    # db = DataBase()
    # settlements = db.get_settlements()
    # for settlement in settlements:
    #     pl = wkb.loads(bytes(settlement.poly.data))
    #     print(settlement.name)
    #     print(Point(82.9346, 55.0415).distance(Point(84.9744, 56.4977)))
    #     print(pl.distance(Point(88.443438, 69.287984)))
    #     break
    # db = DataBase()
    # l = make_list_settlements()
    to_json()
    # data = from_json('settlement_out.json')
    # # print(data)
    # count = 0
    # for key in data['settlements']:
    #     # print(data['settlements'][key])
    #     # break
    #     if data['settlements'][key]['poly']:
    #         count += 1
    # print(count)

#run()



# fetch_settlement_polygon(f'{path_settlement_polygon}/*/*.shp')


