# -*- coding: utf-8 -*-

from sqlalchemy.schema import (Column, MetaData, Table)

from cdsoss.db.sqlalchemy.migrate_repo.schema import (
    Boolean, DateTime, Integer, BigInteger, String, Text, create_tables, drop_tables)  # noqa


def define_region_table(meta):
    region = Table('region',
                   meta,
                   Column('id', String(36), primary_key=True, nullable=False),
                   Column('name', String(36), nullable=False),
                   Column('mgmt_ip', String(255), nullable=False),
                   Column('mgmt_port', Integer(), nullable=False),
                   Column('mgmt_user', String(36), nullable=False),
                   Column('mgmt_passwd', String(36), nullable=False),
                   Column('enable', Boolean(), default=True),
                   Column('created_at', DateTime(), nullable=False),
                   Column('updated_at', DateTime()),
                   Column('deleted_at', DateTime()),
                   Column('deleted',
                           Boolean(),
                           nullable=False,
                           default=False,
                           index=True),
                   mysql_engine='InnoDB',
                   mysql_charset='utf8',
                   extend_existing=True)

    return region


def upgrade(migrate_engine):
    meta = MetaData()
    meta.bind = migrate_engine
    tables = [define_region_table(meta)]
    create_tables(tables)


def downgrade(migrate_engine):
    meta = MetaData()
    meta.bind = migrate_engine
    tables = [define_region_table(meta)]
    drop_tables(tables)
