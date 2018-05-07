from __future__ import absolute_import
import sys
sys.path.append('E:/code/cdsoss/cdsoss')

from cdsoss.celery import app
from celery.utils.log import get_task_logger
from cdsoss.db.sqlalchemy import api as db_api
from cdsoss import constants

from cdsoss.client.cdnsdk import cdn_distribution
from cdsoss import config
logger = get_task_logger(__name__)


@app.task
def create_cdn(cdn_domain, origin_domain):
	cdn_dis = cdn_distribution.Distribution()
	cdn_dis.get_distribution("bcb7536581ce17a71afa89b6e52e62b4")
	pass

