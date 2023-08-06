import os
import time

from geopandas import read_file
from fiona import open as fopen
import fnmatch

from shapely import wkb
from shapely.geometry import shape, Point

from config import path_to_files
from process_fire.base.log import error_wraps
from process_fire.loader_data.load_poly_settlement.settlement_load import make_list_settlements
from process_fire.base.database import DataBase
from process_fire.base.models import Settlement, TechnogenicZone, District, Subject, FireValue


def read_shp_tech_zone(): # Work
    with fopen(f'{path_to_files}/Fakela/fakela_POLIGON_2023_.shp') as data:
        # print(data.schema)
        for row in data:
            # print(row['geometry']['coordinates'])
            # break
            yield str(shape(row['geometry']))


def read_shp_settlement():  # Work
    list_files = os.listdir(f'{path_to_files}/Nas_punkt')

    for file in list_files:
        if fnmatch.fnmatch(file, '*.shp'):
            with fopen(f'{path_to_files}/Nas_punkt/{file}') as data:
                # pprint.pprint(data.schema)
                for row in data:
                    geometry = shape(row['geometry'])
                    name = row['properties']['NAME']
                    # break
                    yield geometry, name


def read_shp_district(): # Work
    with fopen(f'{path_to_files}/Subject/adm6_district.shp') as data:
        # pprint.pprint(data.schema)
        count = 0
        for row in data:
            count += 1

            name_t = row['properties']['NAME']
            oktmo_name = row['properties']['OKTMO_NAME']
            okato_name = row['properties']['OKATO_NAME']
            if name_t and okato_name and oktmo_name:

                oktmo_name = oktmo_name.replace('00', '')
                if ('городской округ' in name_t.lower() or
                      'городской округ' in oktmo_name.lower() or
                      'городской округ' in okato_name.lower()):
                    name = name_t
                elif ('поселок' in name_t.lower() or
                         'поселок' in oktmo_name.lower() or
                         'поселок' in okato_name.lower()):
                    name =  oktmo_name
                elif ('район' in name_t.lower() or
                         'район' in oktmo_name.lower() or
                         'район' in okato_name.lower()):
                    # print(name_t, '-', okato_name, '-', oktmo_name)
                    if ('район' in name_t.lower()):
                        name = name_t.split(' ')[0]
                    else:
                        name = name_t
                elif ('город' in name_t.lower().split(' ') or
                         'город' in oktmo_name.lower().split(' ') or
                         'город' in okato_name.lower().split(' ')):
                    name = oktmo_name
                elif ('округ' in name_t.lower() or
                      'округ' in oktmo_name.lower() or
                      'округ' in okato_name.lower()):

                    temp = name_t.lower().split(' ')[0]
                    if not('ий' == temp[len(temp)-2:len(temp)] or 'ый' == temp[len(temp)-2:len(temp)]):
                        name = 'Округ ' + name_t
                    else:
                        name = name_t

                elif ('зато' in name_t.lower() or
                      'зато' in oktmo_name.lower() or
                      'зато' in okato_name.lower()):
                    name = oktmo_name
                else:
                    if not ('новая земля' in name_t.lower()):
                        name = 'город '+name_t
                    else:
                        name = name_t

            try:
                geometry = shape(row['geometry'])

                try:
                    name_part_id = row['properties']['ADM4_NAME']
                    if name_part_id:
                        part_id = name_part_id.split(' ')[0]
                        part_id = int(part_id)
                        adm4_id = int(str(row['properties']['ADM4_ID'])+str(part_id))
                        # print(adm4_id)
                except TypeError:
                    adm4_id = row['properties']['ADM4_ID']
                except ValueError:
                    adm4_id = row['properties']['ADM4_ID']

                adm_id = row['properties']['ID']

                yield adm_id, adm4_id, name, geometry
            except ValueError:
                continue

        # print('count', count)

@error_wraps
def read_shp_file(): #region # Work
    data = read_file(f'{path_to_files}/Subject/adm4_region.shp')

    count = 0
    for index, row in data.iterrows():
        count += 1
        adm_id, name, geometry = row['OSM_ID'], row['NAME'], row['geometry']
        yield adm_id, name, geometry


class LoadToDataBase:
    district_list = None
    subject_list = None

    def __init__(self):
        self.db = DataBase()

        self.db.create_tables()
        self.db.create_function_insert_district()
        self.db.create_trigger_settlement_ins()
        self.db.create_function_send_notify_process()
        self.db.create_trigger_fire_value_change()
        self.db.create_index(FireValue.__tablename__, 'datetime_id')

    def fetch_subjects_data(self):
        out_list = []

        for subject in self.db.get_subjects():
            poly = wkb.loads(bytes(subject.poly.data))
            out_list.append({
                'id': subject.id,
                'poly': poly,
            })

        return out_list

    def fetch_districts_data(self):
        out_list = []

        for district in self.db.get_districts():
            poly = wkb.loads(bytes(district.poly.data))
            out_list.append({
                'id': district.id,
                'poly': poly,
                'subject_id': district.subject_id,
            })

        return out_list

    def write_subject_shp(self):
        # print(f'{path_to_files}/Subject/adm4_region.shp')
        # print(f'{path_to_files}/Subject/adm4_region.shp')
        # print(f'{path_to_files}/Subject/adm4_region.shp')
        # print(f'{path_to_files}/Subject/adm4_region.shp')
        # print(f'{path_to_files}/Subject/adm4_region.shp')
        # return
        l_s = []
        print('-> Subject. Load...')
        for adm_id, name, geometry in read_shp_file():
            subject = Subject(
                adm_id=adm_id,
                name=name,
                poly=str(geometry),
            )
            l_s.append(subject)
        self.db.insert_all(l_s)

        print('-> -> Data is inserted')

    # @error_wraps
    def write_district(self):
        l_s = []
        print('-> District. Load...')
        for adm6, adm4_id, name, geometry in read_shp_district():
            if geometry and name and adm4_id:
                subject_id = self.db.get_by_adm_id(Subject, adm4_id)[0]
                if subject_id:
                    district = District(
                        name=name,
                        poly=str(geometry),
                        subject_id=subject_id
                    )
                    l_s.append(district)
        print('ALL OK --0|-')
        self.db.insert_all(l_s)

        print('-> -> Data is inserted')

    def fetch_district_id_of_settlement(self, point):
        subject_id = 0

        # print('Start function')
        # start = time.perf_counter()
        for subject in self.subject_list:
            if subject['poly'].contains(Point(point)):
                subject_id = subject['id']
                # print('-', subject_id)
                break
        # end = time.perf_counter()
        # print(f'Time of work - {(end - start):.4f}s')
        # if end - start > 0.05:
        #     print(subject_id)
        if subject_id == 0:
            return None

        for district in self.district_list:
            if district['subject_id'] == subject_id:
                if district['poly'].contains(point):
                    return district['id']

        return None

    def write_settlement_only_point(self):
        l_s = []

        print('-> Settlement. Load...')
        for geometry, name in read_shp_settlement():
            if name:
                l_s.append(Settlement(
                    name=name,
                    point=str(geometry),
                ))

        self.db.insert_all(l_s)
        print('-> -> Data is inserted')

    def write_settlement_with_point_polygon(self):
        print('-> Settlement. Load...')
        l = make_list_settlements(
            f'{path_to_files}/Nas_punkt_polygon', # polygons
            f'{path_to_files}/Nas_punkt', # points
        )
        settlements = [
            Settlement(
                name=item['name'],
                point=str(item['point']),
                poly=str(item['poly']) if item['poly'] is not None else None,
                type=item['type'],
                population=item['population'] if str(item['population']).isdigit() else None
            )
        for item in l]

        self.db.insert_all(settlements)
        print('-> -> Data is inserted')

    def write_technogenic_zone(self):
        l_s = []
        print('-> Tech zone. Load...')
        for geometry in read_shp_tech_zone():
            if geometry:
                l_s.append(TechnogenicZone(
                    poly=geometry,
                ))
        self.db.insert_all(l_s)
        print('-> -> Data is inserted')

    def get_subject(self, value):
        item = self.db.session.query(Subject).filter(Subject.name == value).first()
        return item

    def write_tag_to_regions(self):
        tags = {
            'ALTAY': 'Алтайский край',
            'BUR': 'Республика Бурятия',
            'GALTAY': 'Республика Алтай',
            'IRK': 'Иркутская область',
            'KEM': 'Кемеровская область',
            'KHAK': 'Республика Хакасия',
            'HMAO': 'Ханты-Мансийский автономный округ - Югра',
            'KRSN': 'Красноярский край',
            'NSK': 'Новосибирская область',
            'OMSK': 'Омская область',
            'SAHA': 'Республика Саха (Якутия)',
            'TOMSK': 'Томская область',
            'TUVA': 'Республика Тыва',
            'TUM': 'Тюменская область',
            'YANAO': 'Ямало-Ненецкий автономный округ',
            'ZAB': 'Забайкальский край',
        }
        # print(self.get_subject('Донецкая Народная республика').tag)
        for tag in tags:
            # print(tags[tag])
            try:
                item = self.get_subject(tags[tag])
                item.tag = tag
                self.db.session.flush()
                self.db.session.commit()
            finally:
                self.db.session.close()
