# -*- coding: utf-8 -*-

from sqlalchemy.schema import (Column, MetaData, Table)

from cdsoss.db.sqlalchemy.migrate_repo.schema import (
    Boolean, DateTime, Integer, BigInteger, String, Text, create_tables, drop_tables)  # noqa


def define_namespace_table(meta):
    namespace = Table('namespace',
                   meta,
                   Column('id', String(36), primary_key=True, nullable=False),
                   Column('customer_id', String(36), nullable=False, index=True),
                   Column('customer_name', String(255), nullable=False),
                   Column('project_id', String(36), index=True),
                   Column('user_id', String(36), index=True),
                   Column('user_name', String(255)),
                   Column('name', String(255), nullable=False),
                   Column('bkt_name', String(255), nullable=False, index=True),
                   Column('type', String(36), nullable=False),
                   Column('region_id', String(36), nullable=False),
                   Column('is_version', Boolean(), default=True),
                   Column('version_day', Integer(), default=90),
                   Column('account', String(255), nullable=False),
                   Column('account_pwd', String(255), nullable=False),
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

    return namespace


def upgrade(migrate_engine):
    meta = MetaData()
    meta.bind = migrate_engine
    tables = [define_namespace_table(meta)]
    create_tables(tables)


def downgrade(migrate_engine):
    meta = MetaData()
    meta.bind = migrate_engine
    tables = [define_namespace_table(meta)]
    drop_tables(tables)
