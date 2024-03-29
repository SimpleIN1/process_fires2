import datetime
import functools
import math
import pprint
import sys
import time

from numba import jit

from shapely import wkb
from shapely.geometry import Point, Polygon, LinearRing, LineString
from shapely.ops import nearest_points

from process_fire.base.database import DataBase
from process_fire.base.decorators import time_of_work_wraps
from process_fire.base.log import error_wraps
from process_fire.process_event_pq.calculating_distance import operate_distance


class ProcessFirePoint:

    def __init__(self):
        print('__init__ ProcessFirePoint')
        self.db = DataBase()
        self.db.create_tables()
        self.settlements_dict = {}
        self.settlement_polygons = self.create_polygon_settlement_district()
        self.technogenic_zones = self.fetch_tech_zones_data()
        self.settlements = self.fetch_settlements_data()
        self.subjects = self.fetch_subjects_data()
        self.districts = self.fetch_districts_data()
        self.__count = 0

    def fetch_settlements_data(self):
        out_list = []

        for settlement in self.db.get_settlements():
            point = Point(wkb.loads(bytes(settlement.point.data)))

            if settlement.poly:
                poly = wkb.loads(bytes(settlement.poly.data))
            else:
                poly = None

            x, y = point.xy
            out_list.append({
                'id': settlement.id,
                'longitude': x[0],
                'latitude': y[0],
                'poly': poly,
            })
        print('Settlements is loaded...')
        return out_list

    def fetch_districts_data(self):
        # out_list = []
        out_dict = {}

        for district in self.db.get_districts():
            poly = wkb.loads(bytes(district.poly.data))
            # out_list.append({
            #     'id': district.id,
            #     'poly': poly,
            #     'subject_id': district.subject_id,
            # })
            out_dict[district.id] = {
                'poly': poly,
                'subject_id': district.subject_id,
            }

        print('Districts is loaded..')
        return out_dict #out_list

    def fetch_tech_zones_data(self):
        out_list = []

        for zone in self.db.get_tech_zones():
            poly = wkb.loads(bytes(zone.poly.data)) #Polygon()
            # print(type(poly) is Polygon)
            out_list.append(
                poly
            )
        print('Tech zones is loaded...')
        return out_list

    def fetch_subjects_data(self):
        out_list = []

        for subject in self.db.get_subjects():
            poly = wkb.loads(bytes(subject.poly.data))
            out_list.append({
                'id': subject.id,
                'poly': poly,
            })
        print('Subjects is loaded...')
        return out_list

    def operate_distance_not_working(self, longitude, latitude):
        min_distance = sys.maxsize
        id_min_stln = 0
        long = None
        lat = None
        list_id_settlement = []

        # print('Start function')
        # start = time.perf_counter()

        for settlement in self.settlements:

            distance = None
            if not settlement['poly']:
                point_settlement = (settlement['latitude'], settlement['longitude'])
            else:
                if settlement['poly'].contains(Point(longitude, latitude)):
                    distance = 0
                else:
                    _, point = nearest_points(Point(longitude, latitude), settlement['poly'])
                    point_settlement = (point.x, point.y)

            if not distance == 0:
                distance = operate_distance(
                    latitude, longitude,
                    point_settlement[0], point_settlement[1]
                )

            if min_distance > distance:
                min_distance = distance
                id_min_stln = settlement['id']
                long = settlement['longitude']
                lat = settlement['latitude']
            if distance < 5:
                list_id_settlement.append(int(settlement['id']))

        # end = time.perf_counter()
        # print(f'Time of work - {(end - start):.4f}s')

        return id_min_stln, min_distance, round(long, 5), round(lat, 5), list_id_settlement

    def create_list_point_and_poly_settlement(self):
        settlements = self.db.get_settlements()

        print('-> create list point and poly settlement')
        for settlement in settlements:
            if not self.settlements_dict.get(settlement.district_id):
                self.settlements_dict[settlement.district_id] = {}
            point = Point(wkb.loads(bytes(settlement.point.data)))

            if not self.settlements_dict[settlement.district_id].get('points'):
                self.settlements_dict[settlement.district_id]['points'] = []
            self.settlements_dict[settlement.district_id]['points'].append(
                point
            )

            if not self.settlements_dict[settlement.district_id].get('ids_settlement'):
                self.settlements_dict[settlement.district_id]['ids_settlement'] = {}
            self.settlements_dict[settlement.district_id]['ids_settlement'][settlement.id] = {
                'poly': (wkb.loads(bytes(settlement.poly.data)) if settlement.poly else None),
                'point': point,
            }

        return self.settlements_dict

    def create_polygon_settlement_district(self):
        list_poly = []
        lists_point = self.create_list_point_and_poly_settlement()
        # pprint.pprint(out_dict)
        print('-> create polygon settlement district')
        for key in lists_point:
            if len(lists_point[key]['points']) > 2:
                geometry = Polygon(lists_point[key]['points'])
            elif len(lists_point[key]['points']) == 2:
                geometry = LineString(lists_point[key]['points'])
            else:
                geometry = lists_point[key]['points'][0]

            list_poly.append({
                'district_id': key,
                'poly': geometry,
            })
        return list_poly

    # @time_of_work_wraps
    def operate_distance(self, point, subject_id):

        list_poly_settlement = []
        min = sys.maxsize
        dict = None

        # print('-------')
        for item in self.settlement_polygons:
            if self.districts[item['district_id']]['subject_id'] == subject_id:
                p1, p2 = nearest_points(point, item['poly'])
                distance = operate_distance(p1.y, p1.x, p2.y, p2.x) # здесь ошибка была # done
                if math.isnan(distance):
                    distance=0

                # if self.districts[item['district_id']]['subject_id'] == subject_id:
                if min > distance:
                    min = distance
                    dict = item
                if distance < 5 and item['district_id'] not in list_poly_settlement:
                    list_poly_settlement.append(item['district_id'])

        # print(distance, point)
        # print(dict)

        if dict and dict['district_id'] not in list_poly_settlement \
                 and self.districts[dict['district_id']]['subject_id'] == subject_id:
            list_poly_settlement.append(dict['district_id'])

        list_settlement_id_least_5 = []
        dict_settlement = {}
        min_distance_settlement = sys.maxsize

        for dis_id in list_poly_settlement:
            ids_settlement = self.settlements_dict[dis_id]['ids_settlement']

            distance = None
            for key_id in ids_settlement:
                if ids_settlement[key_id]['poly']:
                    _, p = nearest_points(point, ids_settlement[key_id]['poly'])
                    if p.contains(point):
                        distance = 0
                else:
                    p = ids_settlement[key_id]['point']

                if not distance == 0:
                    distance = operate_distance(p.y, p.x, point.y, point.x) # здесь тоже # done
                # print(distance, key_id, point)
                if min_distance_settlement > distance:
                    min_distance_settlement = distance
                    point_settlemnt = ids_settlement[key_id]['point']

                    dict_settlement['longitude'] = point_settlemnt.x # поменять
                    dict_settlement['latitude'] = point_settlemnt.y # местами x <-> y # done
                    dict_settlement['id_settlement'] = key_id

                if distance <= 5:
                    distance = None
                    list_settlement_id_least_5.append(key_id)

        if dict_settlement:
            dict_settlement['min_distance_settlement'] = min_distance_settlement
            dict_settlement['list_least_5'] = list_settlement_id_least_5

        # return \
        #     dict_settlement['id_settlement'], \
        #     min_distance_settlement, \
        #     dict_settlement['longitude'], \
        #     dict_settlement['latitude'], \
        #     list_settlement_id_least_5
        # print('-----1-------')
        return dict_settlement

    # @time_of_work_wraps
    def is_tech_zone(self, point: Point):
        for zone in self.technogenic_zones: #self.db.get_tech_zones():
            # print(type(zone))
            # poly = wkb.loads(bytes(zone.poly.data))
            if zone.contains(point):
                return True
        return False

    # @time_of_work_wraps
    def entry_in_district(self, longitude, latitude):

        subject_id = 0
        for subject in self.subjects:
            if subject['poly'].contains(Point(longitude, latitude)):
                subject_id = subject['id']
                break

        if subject_id == 0:
            return None, None

        for district_key in self.districts:
            district = self.districts[district_key]
            if district['subject_id'] == subject_id:
                if district['poly'].contains(Point(longitude, latitude)):
                    return district_key, subject_id

        return None, None

    # @time_of_work_wraps
    def calculate_directly(self, longitude, latitude, lon_point, lat_point): # work
        # print(longitude, latitude, lon_point, lat_point)
        if longitude == lon_point and latitude > lat_point:
            directly_from_stlm = 1 # C
        elif longitude == lon_point and latitude < lat_point:
            directly_from_stlm = 2 # Ю
        elif longitude > lon_point and latitude == lat_point:
            directly_from_stlm = 3 # В
        elif longitude < lon_point and latitude == lat_point:
            directly_from_stlm = 4 # З
        elif longitude > lon_point and latitude > lat_point:
            directly_from_stlm = 5 # C-B
        elif longitude < lon_point and latitude > lat_point:
            directly_from_stlm = 6 # C-З
        elif longitude > lon_point and latitude < lat_point:
            directly_from_stlm = 7 # Ю-B
        elif longitude < lon_point and latitude < lat_point:
            directly_from_stlm = 8 # Ю-З:
        else:
            directly_from_stlm = None
        return directly_from_stlm

    # @time_of_work_wraps
    #@error_wraps
    def run_process(self, id_fire_value, longitude, latitude):

        tech = self.is_tech_zone(Point(longitude, latitude))
        district_id, subject_id = self.entry_in_district(longitude, latitude)

        if district_id and tech == False: # correct not tech

            # id_min_stln, min_distance, long, lat, list_id_settlement = self.operate_distance(Point(longitude, latitude),subject_id)

            dict_settlement = self.operate_distance(Point(longitude, latitude),subject_id)

            # if dict_settlement:
            id_min_stln = dict_settlement.get('id_settlement')
            min_distance = dict_settlement.get('min_distance_settlement')
            long = dict_settlement.get('longitude')
            lat = dict_settlement.get('latitude')
            list_id_settlement = dict_settlement.get('list_least_5')

            if dict_settlement:
                if len(list_id_settlement) != 0: # or list_id_settlement != []

                    self.db.insert_settlements(
                        id_fire_value=id_fire_value,
                        list_settlement=list_id_settlement
                    )

            directly = None
            if dict_settlement:
                directly = self.calculate_directly(longitude, latitude, long, lat)
                # print('directly -', directly)
            if True:
                self.db.update_fire_value(id_fire_value, tech, min_distance, id_min_stln, district_id, directly)

        else:
            self.db.update_tech_zone(id_fire_value, tech)
        self.__count+=1
        if self.__count%1000==0:
            print(f'->|->1000 fire values were processed ->|{id_fire_value}|<-')
