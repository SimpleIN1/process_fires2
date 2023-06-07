
from sqlalchemy import Column, Integer, ForeignKey, Numeric, DateTime, String, Boolean, SmallInteger
from geoalchemy2 import Geometry
from process_fire.base.base import Base


class DateTm(Base):
    __tablename__ = "date_time"

    id = Column(Integer, primary_key=True, unique=True)
    datetime = Column(DateTime(timezone=False), unique=True)


class FireValue(Base):
    __tablename__ = "fire_value"

    id = Column(Integer, primary_key=True, unique=True)
    temperature = Column(Numeric(5, 2))
    longitude = Column(Numeric(8, 5))
    latitude = Column(Numeric(8, 5))
    datetime_id = Column(Integer, ForeignKey('date_time.id'))

    tech = Column(Boolean)

    distance_to_stln = Column(Numeric(10, 3))
    settlement_id = Column(Integer, ForeignKey('settlement.id'))

    district_id = Column(Integer, ForeignKey('district.id'))

    satellite = Column(String(20))
    round = Column(Integer)
    alg_name = Column(String(20))

    directly_from_stlm = Column(SmallInteger)


class Settlement(Base):
    __tablename__ = 'settlement'

    id = Column(Integer, primary_key=True, unique=True)
    name = Column(String(70))
    point = Column(Geometry('POINT'), nullable=True)
    poly = Column(Geometry, nullable=True)
    district_id = Column(Integer, ForeignKey('district.id'))
    type = Column(String(20))
    population = Column(Integer)


class SettlementFireValue(Base):
    __tablename__ = 'settlement_fire_value'

    fire_value_id = Column(Integer, ForeignKey('fire_value.id'), primary_key=True)
    settlement_id = Column(Integer, ForeignKey('settlement.id'), primary_key=True)


class Subject(Base):
    __tablename__ = 'subject'

    id = Column(Integer, primary_key=True, unique=True)
    name = Column(String(100))
    adm_id = Column(Integer, unique=True)
    poly = Column(Geometry)
    tag = Column(String(10))


class District(Base):
    __tablename__ = 'district'

    id = Column(Integer, primary_key=True, unique=True)
    name = Column(String(100))
    poly = Column(Geometry)
    subject_id = Column(Integer, ForeignKey('subject.id'))


class TechnogenicZone(Base):
    __tablename__ = 'technogenic_zone'

    id = Column(Integer, primary_key=True)
    poly = Column(Geometry)
