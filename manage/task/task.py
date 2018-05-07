# -*- coding: utf-8 -*-

"""Defines app manager."""
import logging
from cdsoss.db.sqlalchemy import api as db_api

LOG = logging.getLogger(__name__)


def get_task(task_id):
    return db_api.task_get(task_id)

