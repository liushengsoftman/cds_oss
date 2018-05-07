

"""Database setup and migration commands."""

import os

from cdsoss.common import utils
from cdsoss.db.sqlalchemy import api as db_api

IMPL = utils.LazyPluggable(
    'backend',
    config_group='database',
    sqlalchemy='cdsoss.common.db.sqlalchemy.migration')

INIT_VERSION = 0

MIGRATE_REPO_PATH = os.path.join(
    os.path.abspath(os.path.dirname(__file__)),
    'sqlalchemy',
    'migrate_repo',
)


def db_sync(version=None, init_version=0):
    """Migrate the database to `version` or the most recent version."""
    return IMPL.db_sync(engine=db_api.get_engine(),
                        abs_path=MIGRATE_REPO_PATH,
                        version=version,
                        init_version=init_version)
