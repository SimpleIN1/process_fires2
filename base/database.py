import logging
from datetime import datetime

import sqlalchemy.exc
from shapely.geometry import shape
from sqlalchemy import inspect, text, DDL, event


from process_fire.base.base import SessionLocal, engine, Base
from process_fire.base.decorators import time_of_work_wraps
from process_fire.base.log import error_wraps
from process_fire.base.models import DateTm, FireValue, Subject, \
                   Settlement, SettlementFireValue, District, \
                   TechnogenicZone
from process_fire import config



class FuncSqlRow:

    @error_wraps
    def execute_row(self, row):
        self.session.execute(
            text(row)
        )
        self.session.commit()

    def create_function_insert_district(self):
        self.execute_row(config.psql_row_create_function_insert_district)

    def create_trigger_settlement_ins(self):
        self.execute_row(config.psql_row_create_trigger_settlement_ins)

    def create_function_send_notify_process(self):
        self.execute_row(config.psql_row_create_function_send_notify_process)

    def create_trigger_fire_value_change(self):
        self.execute_row(config.psql_row_create_trigger_fire_value_change)

    def drop(self, type_func, name):
        return 'drop {} {}'.format(type_func, name)

    def drop_trigger_settlement_ins(self):
        self.execute_row(
            self.drop('trigger', config.name_trigger_settlement_ins)
        )

    def drop_function_insert_district(self):
        self.execute_row(
            self.drop('function', config.name_function_insert_district)
        )

    def drop_trigger_fire_value_change(self):
        self.execute_row(
            self.drop('trigger', config.name_trigger_fire_value_change)
        )

    def drop_function_send_notify_process(self):
        self.execute_row(
            self.drop('function', config.name_function_send_notify_process)
        )

    def create_index(self, table_name, attribute):
        self.execute_row('create index CONCURRENTLY on {} ({});'.format(table_name, attribute))


class DataBase(FuncSqlRow):

    def __init__(self):
        self.session = SessionLocal()
        super().__init__()

    def create_tables(self):
        tables = inspect(engine).get_table_names()

        print('-> create tables')
        if not DateTm.__tablename__ in tables or \
                not FireValue.__tablename__ in tables or \
                not Subject.__tablename__ in tables or \
                not Settlement.__tablename__ in tables or \
                not SettlementFireValue.__tablename__ in tables or \
                not District.__tablename__ in tables or \
                not TechnogenicZone.__tablename__ in tables:

            Base.metadata.create_all(engine)
        print('-> Create tables is performed')

    def drop_all_tables(self):
        # SettlementFireValue.__table__.drop(engine)
        # Settlement.__table__.drop(engine)
        print('-> Drop tables')
        # print(inspect(engine).get_table_names())
        Base.metadata.drop_all(bind=engine, tables=[
            FireValue.__table__,
            Subject.__table__,
            Settlement.__table__,
            SettlementFireValue.__table__,
            District.__table__,
            TechnogenicZone.__table__,
            # Satellite.__table__,
            DateTm.__table__
        ])
        print('-> Drop tables is performed')

    def get_tech_zones(self):
        query = self.session.query(TechnogenicZone).all()
        return query

    def get_settlements(self):
        query = self.session.query(Settlement).all()
        return query

    def get_districts(self):
        query = self.session.query(District).all()
        return query

    def get_subjects(self):
        query = self.session.query(Subject).all()
        return query

    #@time_of_work_wraps
    def insert_settlements(self, id_fire_value, list_settlement):
        try:
            self.session.add_all(
                [SettlementFireValue(fire_value_id=id_fire_value, settlement_id=id_settlement) for id_settlement in list_settlement]
            )
            self.session.commit()
        except Exception as e:
            logging.error(f'insert_settlements - {e}')
            print('insert_settlements -', e)

    def get_fire_value_by_id(self, id):
        return self.session.query(FireValue).filter(FireValue.id == id).first()

    #@time_of_work_wraps
    def update_fire_value(self, id_fire_value, tech, min_distance, id_min_stln, district_id, directly):
        try:
            fire_value = self.get_fire_value_by_id(id_fire_value)
            fire_value.tech = tech
            fire_value.distance_to_stln = min_distance
            fire_value.settlement_id = id_min_stln
            fire_value.district_id = district_id
            fire_value.directly_from_stlm = directly

            self.session.flush()
            self.session.commit()
        except Exception as e:
            logging.error(e)
            print('update_fire_value -', e)

    def update_tech_zone(self, id_fire_value, tech):
        try:
            fire_value = self.get_fire_value_by_id(id_fire_value)
            fire_value.tech = tech

            self.session.flush()
            self.session.commit()
        except Exception as e:
            logging.error(f'update_fire_value_tech - {e}')
            print('update_fire_value_tech -', e)

    def get_by_adm_id(self, model, value):
        item = self.session.query(model.id).filter(model.adm_id == value).first()
        return item

    def get_by_id(self, model, id):
        item = self.session.query(model).filter(model.id == id).first()
        return item

    def insert_all(self, list_subjects):
        try:
            self.session.add_all(list_subjects)
            self.session.commit()
        except Exception as e:
            logging.error(e)
            print('--|0-', e)
        finally:
            self.session.close()

    def get_or_create(self, model, **kwargs):
        # print(kwargs)
        instance = self.session.query(model).filter_by(**kwargs).one_or_none()
        if instance:
            return instance
        else:
            instance = model(**kwargs)
            self.session.add(instance)
            self.session.commit()
            return instance

    @classmethod
    def fetch_key_temperature(cls, schema):
        for key in schema['properties']:
            if 'temperat' in key:
                return key
        return None

    @error_wraps
    def insert_data_fires(self, date_time: datetime, data_fires, **kwargs):
        # dt = DateTm(datetime=date_time)
        # self.session.add(dt)
        # self.session.commit()

        dt = self.get_or_create(model=DateTm, datetime=date_time)
        # if not dt
        attribute_name = data_fires.fields[3][0] 
        l_s = [FireValue(
            temperature=row.record[attribute_name],#[self.fetch_key_temperature(data_fires.schema)], #['temperatur'],
            latitude=shape(row.shape).y,
            longitude=shape(row.shape).x,
            datetime_id=dt.id,
            satellite=kwargs.get('satellite'),
            round=kwargs.get('round'),
            alg_name=kwargs.get('alg_name')
        ) for row in data_fires]

        self.insert_all(l_s)


# db = DataBase()
# # db.create_function_send_notify_process()
# # db.create_trigger_fire_value_change()
# db.drop_all_tables()
# db.drop_function_send_notify_process()
# db.drop_function_insert_district()
