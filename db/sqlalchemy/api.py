# -*- coding: utf-8 -*-


"""Defines interface for DB access."""

from cdsoss.common import cfg
import six
from six.moves import xrange
import sqlalchemy
import sqlalchemy.orm as sa_orm
import sqlalchemy.sql as sa_sql
from cdsoss import constants
from cdsoss.common import exception
from cdsoss.db.sqlalchemy import models
from cdsoss.common.db import exception as db_exception
from cdsoss.common.db.sqlalchemy import session
import cdsoss.common.log as os_logging
from cdsoss.common import timeutils
from cdsoss.common.db import options
from cdsoss.common.gettextutils import _


BASE = models.BASE
sa_logger = None
LOG = os_logging.getLogger(__name__)


STATUSES = ['active', 'saving', 'queued', 'killed', 'pending_delete',
            'deleted']

CONF = cfg.CONF

_FACADE = None

def _create_facade_lazily():
    global _FACADE
    if _FACADE is None:
        _FACADE = session.EngineFacade(
            CONF.database.connection,
            **dict(six.iteritems(CONF.database)))
    return _FACADE


def get_engine():
    facade = _create_facade_lazily()
    return facade.get_engine()


def get_session(autocommit=True, expire_on_commit=False):
    facade = _create_facade_lazily()
    return facade.get_session(autocommit=autocommit,
                              expire_on_commit=expire_on_commit)


def clear_db_env():
    """
    Unset global configuration variables for database.
    """
    global _FACADE
    _FACADE = None


def _paginate_query(query, model, limit, sort_keys, marker=None,
                    sort_dir=None, sort_dirs=None):
    """Returns a query with sorting / pagination criteria added.

    Pagination works by requiring a unique sort_key, specified by sort_keys.
    (If sort_keys is not unique, then we risk looping through values.)
    We use the last row in the previous page as the 'marker' for pagination.
    So we must return values that follow the passed marker in the order.
    With a single-valued sort_key, this would be easy: sort_key > X.
    With a compound-values sort_key, (k1, k2, k3) we must do this to repeat
    the lexicographical ordering:
    (k1 > X1) or (k1 == X1 && k2 > X2) or (k1 == X1 && k2 == X2 && k3 > X3)

    We also have to cope with different sort_directions.

    Typically, the id of the last row is used as the client-facing pagination
    marker, then the actual marker object must be fetched from the db and
    passed in to us as marker.

    :param query: the query object to which we should add paging/sorting
    :param model: the ORM model class
    :param limit: maximum number of items to return
    :param sort_keys: array of attributes by which results should be sorted
    :param marker: the last item of the previous page; we returns the next
                    results after this value.
    :param sort_dir: direction in which results should be sorted (asc, desc)
    :param sort_dirs: per-column array of sort_dirs, corresponding to sort_keys

    :rtype: sqlalchemy.orm.query.Query
    :return: The query with sorting/pagination added.
    """

    if 'id' not in sort_keys:
        # TODO(justinsb): If this ever gives a false-positive, check
        # the actual primary key, rather than assuming its id
        LOG.warn(_('Id not in sort_keys; is sort_keys unique?'))

    assert(not (sort_dir and sort_dirs))

    # Default the sort direction to ascending
    if sort_dirs is None and sort_dir is None:
        sort_dir = 'asc'

    # Ensure a per-column sort direction
    if sort_dirs is None:
        sort_dirs = [sort_dir for _sort_key in sort_keys]

    assert(len(sort_dirs) == len(sort_keys))

    # Add sorting
    for current_sort_key, current_sort_dir in zip(sort_keys, sort_dirs):
        sort_dir_func = {
            'asc': sqlalchemy.asc,
            'desc': sqlalchemy.desc,
        }[current_sort_dir]

        try:
            sort_key_attr = getattr(model, current_sort_key)
        except AttributeError:
            raise exception.InvalidSortKey()
        query = query.order_by(sort_dir_func(sort_key_attr))

    default = ''  # Default to an empty string if NULL

    # Add pagination
    if marker is not None:
        marker_values = []
        for sort_key in sort_keys:
            v = getattr(marker, sort_key)
            if v is None:
                v = default
            marker_values.append(v)

        # Build up an array of sort criteria as in the docstring
        criteria_list = []
        for i in xrange(len(sort_keys)):
            crit_attrs = []
            for j in xrange(i):
                model_attr = getattr(model, sort_keys[j])
                default = None if isinstance(
                    model_attr.property.columns[0].type,
                    sqlalchemy.DateTime) else ''
                attr = sa_sql.expression.case([(model_attr != None,
                                              model_attr), ],
                                              else_=default)
                crit_attrs.append((attr == marker_values[j]))

            model_attr = getattr(model, sort_keys[i])
            default = None if isinstance(model_attr.property.columns[0].type,
                                         sqlalchemy.DateTime) else ''
            attr = sa_sql.expression.case([(model_attr != None,
                                          model_attr), ],
                                          else_=default)
            if sort_dirs[i] == 'desc':
                crit_attrs.append((attr < marker_values[i]))
            elif sort_dirs[i] == 'asc':
                crit_attrs.append((attr > marker_values[i]))
            else:
                raise ValueError(_("Unknown sort direction, "
                                   "must be 'desc' or 'asc'"))

            criteria = sa_sql.and_(*crit_attrs)
            criteria_list.append(criteria)

        f = sa_sql.or_(*criteria_list)
        query = query.filter(f)

    if limit is not None:
        query = query.limit(limit)

    return query


def _drop_protected_attrs(model_class, values):
    """
    Removed protected attributes from values dictionary using the models
    __protected_attributes__ field.
    """
    for attr in model_class.__protected_attributes__:
        if attr in values:
            del values[attr]


def region_create(values):
    session = get_session()
    region = {}
    with session.begin():
        if values.get('name', None) is not None:
            region['name'] = values['name']
        if values.get('mgmt_ip', None) is not None:
            region['mgmt_ip'] = values['mgmt_ip']
        if values.get('mgmt_port', None) is not None:
            region['mgmt_port'] = values['mgmt_port']
        if values.get('mgmt_user', None) is not None:
            region['mgmt_user'] = values['mgmt_user']
        if values.get('mgmt_passwd', None) is not None:
            region['mgmt_passwd'] = values['mgmt_passwd']

        region_ref = models.Region()

        region_ref.update(region)

        region_ref.save(session=session)

    return region_get(region_ref.id)


def region_update(id, values):
    session = get_session()
    region = {}
    with session.begin():
        if values.get('name', None) is not None:
            region['name'] = values['name']
        if values.get('mgmt_ip', None) is not None:
            region['mgmt_ip'] = values['mgmt_ip']
        if values.get('mgmt_port', None) is not None:
            region['mgmt_port'] = values['mgmt_port']
        if values.get('mgmt_user', None) is not None:
            region['mgmt_user'] = values['mgmt_user']
        if values.get('mgmt_passwd', None) is not None:
            region['mgmt_passwd'] = values['mgmt_passwd']
        if values.get('enable', None) is not None:
            region['enable'] = values['enable']
            
        query = session.query(models.Region)      
        region_ref = query.filter_by(id=id).one()
        region_ref.update(region)
        region_ref.save(session=session)   
    
        
def region_get(id, force_show_deleted=False):
    session = get_session()
    region_ref = _region_get(id, session,
                             force_show_deleted=force_show_deleted)
    return region_ref.to_dict()


def _region_get(id, session, force_show_deleted=False):
    try:
        query = session.query(models.Region).filter_by(id=id)
        if not force_show_deleted:
            query = query.filter_by(deleted=False)
        region_ref = query.one()
    except sa_orm.exc.NoResultFound:
        msg = (_("No region found with ID %s") % id)
        LOG.error(msg)
        raise exception.NotFound(msg)
    
    return region_ref


def region_list(marker=None, limit=None, sort_key='created_at', sort_dir='desc'):
    session = get_session()
    query = session.query(models.Region)
    
    marker_region = None
    if marker is not None:
        marker_region = _region_get(marker)
        
    #Fetch alarm data from db with paginate.
    sort_keys = ['created_at']
    sort_keys.insert(0, sort_key) if sort_key not in sort_keys else sort_keys
    query = _paginate_query(query, models.Region, limit,
                            sort_keys,
                            marker=marker_region,
                            sort_dir=sort_dir)
    
    result_refs = query.filter_by(deleted=False).all()
    
    results = []
    for result_ref in result_refs:
        results.append(result_ref.to_dict())
        
    return results


def region_delete(id):
    session = get_session()
    try:
        query = session.query(models.Region)
        ref = query.filter_by(id=id).one()
    except sa_orm.exc.NoResultFound:
        msg = (_("No region found with ID %s") % id)
        LOG.error(msg)
        raise exception.NotFound(msg)
    
    ref.delete(session=session)
    
    
def namespace_create(values):
    session = get_session()
    namespace = {}
    with session.begin():
        if values.get('id', None) is not None:
            namespace['id'] = values['id']
        if values.get('customer_id', None) is not None:
            namespace['customer_id'] = values['customer_id']
        if values.get('customer_name', None) is not None:
            namespace['customer_name'] = values['customer_name']
        if values.get('project_id', None) is not None:
            namespace['project_id'] = values['project_id']
        if values.get('user_id', None) is not None:
            namespace['user_id'] = values['user_id']
        if values.get('user_name', None) is not None:
            namespace['user_name'] = values['user_name']
        if values.get('name', None) is not None:
            namespace['name'] = values['name']
        if values.get('bkt_name', None) is not None:
            namespace['bkt_name'] = values['bkt_name']
        if values.get('type', None) is not None:
            namespace['type'] = values['type']
        if values.get('region_id', None) is not None:
            namespace['region_id'] = values['region_id']
        if values.get('is_version', None) is not None:
            namespace['is_version'] = values['is_version']
        if values.get('version_day', None) is not None:
            namespace['version_day'] = values['version_day']
        if values.get('account', None) is not None:
            namespace['account'] = values['account']
        if values.get('account_pwd', None) is not None:
            namespace['account_pwd'] = values['account_pwd']

        namespace_ref = models.Namespace()

        namespace_ref.update(namespace)

        namespace_ref.save(session=session)

    return namespace_get(namespace_ref.id)


def namespace_update(id, values):
    session = get_session()
    namespace = {}
    with session.begin():
        if values.get('name', None) is not None:
            namespace['name'] = values['name']
        if values.get('type', None) is not None:
            namespace['type'] = values['type']
        if values.get('is_version', None) is not None:
            namespace['is_version'] = values['is_version']
        if values.get('version_day', None) is not None:
            namespace['version_day'] = values['version_day']
        if values.get('account_pwd', None) is not None:
            namespace['account_pwd'] = values['account_pwd']
            
        query = session.query(models.Namespace)      
        namespace_ref = query.filter_by(id=id).one()
        namespace_ref.update(namespace)
        namespace_ref.save(session=session)   
    
        
def namespace_get(id, force_show_deleted=False):
    session = get_session()
    namespace_ref = _namespace_get(id, session,
                                   force_show_deleted=force_show_deleted)
    return namespace_ref.to_dict()


def _namespace_get(id, session, force_show_deleted=False):
    try:
        query = session.query(models.Namespace).filter_by(id=id)
        if not force_show_deleted:
            query = query.filter_by(deleted=False)
        namespace_ref = query.one()
    except sa_orm.exc.NoResultFound:
        msg = (_("No namespace found with ID %s") % id)
        LOG.error(msg)
        raise exception.NotFound(msg)
    
    return namespace_ref


def namespace_list(marker=None, limit=None, sort_key='created_at', sort_dir='desc'):
    session = get_session()
    query = session.query(models.Namespace)
    
    marker_namespace = None
    if marker is not None:
        marker_namespace = _namespace_get(marker)
        
    #Fetch alarm data from db with paginate.
    sort_keys = ['created_at']
    sort_keys.insert(0, sort_key) if sort_key not in sort_keys else sort_keys
    query = _paginate_query(query, models.Namespace, limit,
                            sort_keys,
                            marker=marker_namespace,
                            sort_dir=sort_dir)
    
    result_refs = query.all()
    
    results = []
    for result_ref in result_refs:
        results.append(result_ref.to_dict())
        
    return results


def namespace_delete(id):
    session = get_session()
    try:
        query = session.query(models.Namespace)
        ref = query.filter_by(id=id).one()
    except sa_orm.exc.NoResultFound:
        msg = (_("No namespace found with ID %s") % id)
        LOG.error(msg)
        raise exception.NotFound(msg)
    
    ref.delete(session=session)
