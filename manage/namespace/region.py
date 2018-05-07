# -*- coding: utf-8 -*-

import logging
from cdsoss.db.sqlalchemy import api as db_api
LOG = logging.getLogger(__name__)


def get_region(id):
    return db_api.region_get(id)


def list_region():
    return db_api.region_list()


def update_region(id, values):
    db_api.region_update(id, values)
    

def create_region(values):
    db_api.region_create(values)
    
    
def delete_region(id):
    return db_api.region_delete(id)