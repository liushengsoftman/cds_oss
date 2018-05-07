# -*- coding: utf-8 -*-

"""
SQLAlchemy models for cdsoss data
"""

import uuid

from sqlalchemy import BigInteger
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import ForeignKey
from sqlalchemy import Index
from sqlalchemy import Integer
from sqlalchemy.orm import backref, relationship
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy.types import TypeDecorator
from sqlalchemy import UniqueConstraint

from cdsoss.common.db.sqlalchemy import models

from cdsoss.common import timeutils
from cdsoss import constants


BASE = declarative_base()
    

class OSSSimpleBase(models.ModelBase):
    """Simple Base class for OSS Simple Models."""

    __table_args__ = {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8'}
    __table_initialized__ = False
    

    def keys(self):
        return self.__dict__.keys()

    def values(self):
        return self.__dict__.values()

    def items(self):
        return self.__dict__.items()

    def to_dict(self):
        d = self.__dict__.copy()
        d.pop("_sa_instance_state")
        return d
    

class OSSBase(models.ModelBase, models.TimestampMixin):
    """Base class for OSS Models."""

    __table_args__ = {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8'}
    __table_initialized__ = False
    __protected_attributes__ = set([
        "created_at", "updated_at", "deleted_at", "deleted"])

    def save(self, session=None):
        from cdsoss.db.sqlalchemy import api as db_api
        super(OSSBase, self).save(session or db_api.get_session())

    created_at = Column(DateTime, default=lambda: timeutils.utc2local(timeutils.utcnow()),
                        nullable=False)

    updated_at = Column(DateTime, default=lambda: timeutils.utc2local(timeutils.utcnow()),
                        nullable=False, onupdate=lambda: timeutils.utc2local(timeutils.utcnow()))

    deleted_at = Column(DateTime)
    deleted = Column(Boolean, nullable=False, default=False)

    def delete(self, session=None):
        """Delete this object."""
        self.deleted = True
        self.deleted_at = timeutils.utc2local(timeutils.utcnow())
        self.save(session=session)

    def keys(self):
        return self.__dict__.keys()

    def values(self):
        return self.__dict__.values()

    def items(self):
        return self.__dict__.items()

    def to_dict(self):
        d = self.__dict__.copy()
        d.pop("_sa_instance_state")
        return d
                          
                          
class Region(BASE, OSSBase):
    __tablename__ = 'region'
    __table_args__ = (Index('region_deleted_idx', 'deleted'),)

    id = Column(String(36), primary_key=True,
                default=lambda: str(uuid.uuid4()))
    name = Column(String(36), nullable=False)
    mgmt_ip = Column(String(255), nullable=False)
    mgmt_port = Column(Integer(), nullable=False)
    mgmt_user = Column(String(36), nullable=False)
    mgmt_passwd = Column(String(36), nullable=False)
    enable = Column(Boolean(), default=True)


class Namespace(BASE, OSSBase):
    __tablename__ = 'namespace'
    __table_args__ = (Index('namespace_deleted_idx', 'deleted'),
                      Index('namespace_customer_id_idx', 'customer_id'),
                      Index('rnamespace_project_id_idx', 'project_id'),
                      Index('namespace_user_id_idx', 'user_id'),
                      Index('namespace_bkt_name_idx', 'bkt_name'),)

    id = Column(String(36), primary_key=True)
    customer_id = Column(String(36), nullable=False)
    customer_name = Column(String(255), nullable=False)
    project_id = Column(String(36))
    user_id = Column(String(36))
    user_name = Column(String(255))
    name = Column(String(255), nullable=False)
    bkt_name = Column(String(255), nullable=False)
    type = Column(String(36), nullable=False)
    region_id = Column(String(36), nullable=False)
    is_version = Column(Boolean(), default=True)
    version_day = Column(Integer(), default=90)
    account = Column(String(255), nullable=False)
    account_pwd = Column(String(255), nullable=False)
    

def register_models(engine):
    """Create database tables for all models with the given engine."""
    models = (Zone, Site, Pod, App, OpsUser, OpsImage, OpsImageMapping)
    for model in models:
        model.metadata.create_all(engine)


def unregister_models(engine):
    """Drop database tables for all models with the given engine."""
    models = (Zone, Site, Pod, App, OpsUser, OpsImage, OpsImageMapping)
    for model in models:
        model.metadata.drop_all(engine)
        
