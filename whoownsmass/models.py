# database tables and relationships using sqlalchemy

from sqlalchemy import Column, String, Integer, Float, Boolean, Date, ForeignKey, Table, DECIMAL
from sqlalchemy.orm import relationship, declarative_base
from geoalchemy2 import Geometry


Base = declarative_base()


# link table for many-to-many between sites and owners
site_to_owner = Table('site_to_owner', Base.metadata,
                      Column('site_id', ForeignKey('site.id'), primary_key=True),
                      Column('owner_id', ForeignKey('owner.id'), primary_key=True))

officer_to_role = Table('officer_to_role', Base.metadata,
                        Column('officer_id', ForeignKey('officer.id'), primary_key=True),
                        Column('role_name', ForeignKey('role.name'), primary_key=True))


# MODELS
class MetaCorp(Base):
    __tablename__ = "metacorps_network"
    id = Column(String(100), primary_key=True)
    name = Column(String(500))
    val = Column(Integer)
    prop_count = Column(Integer)
    unit_count = Column(Float)
    area = Column(Integer)
    units_per_prop = Column(Float)
    val_per_prop = Column(Float)
    val_per_area = Column(Float)
    company_count = Column(Integer)
    owners = relationship("Owner", back_populates="metacorp")
    companies = relationship("Company", back_populates="metacorp")
    officers = relationship("Officer", back_populates="metacorp")


class Municipality(Base):
    __tablename__ = "muni"
    id = Column(String(250), primary_key=True)
    muni = Column(String(250), nullable=False)
    state = Column(String(25))
    hns = Column(Boolean, default=False, nullable=False)
    mapc = Column(Boolean, default=False, nullable=False)
    geometry = Column(Geometry(geometry_type='MULTIPOLYGON', srid=4326), nullable=False)


class ZipCode(Base):
    __tablename__ = "zip"
    zip = Column(String(50), primary_key=True)
    geometry = Column(Geometry(geometry_type='MULTIPOLYGON', srid=4326), nullable=False)


class BlockGroup(Base):
    __tablename__ = "block_group"
    id = Column(String(12), primary_key=True)
    geometry = Column(Geometry(geometry_type='MULTIPOLYGON', srid=4326), nullable=False)


class Tract(Base):
    __tablename__ = "tract"
    id = Column(String(11), primary_key=True)
    geometry = Column(Geometry(geometry_type='MULTIPOLYGON', srid=4326), nullable=False)


class ParcelPoint(Base):
    __tablename__ = "parcels_point"
    id = Column(String(100), primary_key=True)
    muni_id = Column(String(250), ForeignKey('muni.id'))
    block_group_id = Column(String(12), ForeignKey('block_group.id'))
    tract_id = Column(String(11), ForeignKey('tract.id'))
    lat = Column(Float)
    lng = Column(Float)
    geometry = Column(Geometry(geometry_type='POINT', srid=4326), nullable=False)


class Address(Base):
    __tablename__ = "address"
    id = Column(Integer, primary_key=True)
    addr = Column(String(500))
    start = Column(DECIMAL(precision=100, scale=1))
    end = Column(DECIMAL(precision=100, scale=1))
    body = Column(String(500))
    even = Column(Boolean, default=False)
    muni = Column(String(100))
    postal = Column(String(50))
    state = Column(String(100))
    parcel_id = Column(String(100), ForeignKey('parcels_point.id'))
    parcel = relationship("ParcelPoint")
    owners = relationship("Owner", back_populates="address")
    companies = relationship("Company", back_populates="address")
    officers = relationship("Officer", back_populates="address")
    sites = relationship("Site", back_populates="address")


class Site(Base):
    __tablename__ = "site"
    id = Column(Integer, primary_key=True)
    fy = Column(Integer, nullable=False)
    muni_id = Column(String(250), ForeignKey('muni.id'))
    ls_date = Column(Date)
    ls_price = Column(Integer)
    bld_area = Column(Integer)
    res_area = Column(Integer)
    units = Column(Integer, nullable=False)
    bld_val = Column(Integer, nullable=False)
    lnd_val = Column(Integer, nullable=False)
    use_code = Column(String(20), nullable=False)
    luc = Column(String(10), nullable=False)
    ooc = Column(Boolean, nullable=False)
    condo = Column(Boolean, nullable=False)
    address_id = Column(Integer, ForeignKey('address.id'))
    address = relationship("Address", back_populates="sites")
    owners = relationship("Owner", secondary=site_to_owner, back_populates="sites")


class Company(Base):
    __tablename__ = "company"
    id = Column(Integer, primary_key=True)
    name = Column(String(500))
    company_type = Column(String(500))
    address_id = Column(Integer, ForeignKey('address.id'))
    metacorp_id = Column(String(100), ForeignKey('metacorps_network.id'))
    metacorp = relationship("MetaCorp", back_populates="companies")
    address = relationship("Address", back_populates="companies")


class Owner(Base):
    __tablename__ = "owner"
    id = Column(Integer, primary_key=True)
    name = Column(String(500))
    inst = Column(Boolean)
    trust = Column(Boolean)
    trustees = Column(Boolean)
    address_id = Column(Integer, ForeignKey('address.id'))
    metacorp_id = Column(String(100), ForeignKey('metacorps_network.id'))
    company_id = Column(Integer, ForeignKey('company.id'))
    metacorp = relationship("MetaCorp", back_populates="owners")
    address = relationship("Address", back_populates="owners")
    sites = relationship("Site", secondary=site_to_owner, back_populates="owners")


class Role(Base):
    __tablename__ = "role"
    name = Column(String(500), primary_key=True)
    officers = relationship("Officer", secondary=officer_to_role, back_populates="roles")


class Officer(Base):
    __tablename__ = "officer"
    id = Column(Integer, primary_key=True)
    name = Column(String(500), nullable=True)
    inst = Column(Boolean, default=False, nullable=False)
    company_id = Column(Integer, ForeignKey('company.id'))
    address_id = Column(Integer, ForeignKey('address.id'))
    metacorp_id = Column(String(100), ForeignKey('metacorps_network.id'))
    metacorp = relationship("MetaCorp", back_populates="officers")
    address = relationship("Address", back_populates="officers")
    roles = relationship("Role", secondary=officer_to_role, back_populates="officers")


# class User(Base):
#     __tablename__ = "user"
#     id = Column(Integer, primary_key=True, index=True)
#     username = Column(String(150), unique=True, index=True, nullable=False)
#     email = Column(String(255), unique=True, index=True)
#     full_name = Column(String(255))
#     hashed_password = Column(String(255), nullable=False)
#     is_active = Column(Boolean, default=True, nullable=False)
#     is_admin = Column(Boolean, default=False, nullable=False)
