# -*- coding: utf-8 -*-

import copy
import functools
import eventlet
from cdsoss.common import cfg
import six.moves.urllib.parse as urlparse
from webob.exc import HTTPBadRequest
from webob.exc import HTTPConflict
from webob.exc import HTTPForbidden
from webob.exc import HTTPNotFound
from webob.exc import HTTPRequestEntityTooLarge
from webob import Response

from cdsoss.api import policy
import cdsoss.api.v1
from cdsoss.api.v1 import filters
from cdsoss.common import exception
from cdsoss.common import property_utils
from cdsoss.common import wsgi
#from cdsoss import notifier
import cdsoss.common.log as logging

#from cdsoss.manager.glnace import image as image_manager
from cdsoss.db.sqlalchemy import api as db_api

LOG = logging.getLogger(__name__)

def para_check(outer_key=None, must_key=[], mustnot_key=[]):
    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            req = args[1]
            if not kwargs:
                msg = _("Http request body can't be null.")
                LOG.error(msg)
                raise HTTPBadRequest(explanation=msg,
                             request=req,
                             content_type="text/plain")
            body = kwargs.get('body')
            values = body.get(outer_key,{})
            err_key = []
            must_attrs = copy.deepcopy(must_key)
            for k,v in values.iteritems():
                if k in must_attrs:
                    must_attrs.pop(must_attrs.index(k))
                    if not v:
                        msg = _("Attr %s need a value.") % k
                        LOG.error(msg)
                        raise HTTPBadRequest(explanation=msg,
                                     request=req,
                                     content_type="text/plain")
                else:
                    err_key.append(k)
            if mustnot_key:
                err_key = set(err_key) - set(mustnot_key)
                err_key = [ x for x in iter(err_key)]
            if err_key:
                msg = _("Attr %s be error key.") % '|'.join(err_key)
                LOG.error(msg)
                raise HTTPBadRequest(explanation=msg,
                                     request=req,
                                     content_type="text/plain")
            if must_attrs:
                msg = _("Attr %s be must need.") % '|'.join(must_attrs)
                LOG.error(msg)
                raise HTTPBadRequest(explanation=msg,
                                     request=req,
                                     content_type="text/plain")
            
            return f(*args, **kwargs)
        return wrapper
    return decorator

class BaseController(object):
    """
    WSGI controller for logs resource in cdsoss v1 API

    The logs resource API is a RESTful web service for log data. The API
    is as follows::

        GET /<USER_ID>/logs -- Returns a set of brief metadata about logs
        
    """

    def __init__(self):
        #self.notifier = notifier.Notifier()
        self.policy = policy.Enforcer()
        self.pool = eventlet.GreenPool(size=1024)
        if property_utils.is_property_protection_enabled():
            self.prop_enforcer = property_utils.PropertyRules(self.policy)
        else:
            self.prop_enforcer = None

    def _enforce(self, req, action):
        """Authorize an action against our policies"""
        try:
            self.policy.enforce(req.context, action, {})
        except exception.Forbidden:
            raise HTTPForbidden()
        
    #def _get_ksclient(self):
    #    from keystoneclient.v2_0 import client
    #    return client.Client(username= CONF.keystone_authtoken.admin_user,
    #                         password= CONF.keystone_authtoken.admin_password,
    #                         tenant_name = CONF.keystone_authtoken.admin_tenant_name,
    #                         auth_url=CONF.keystone_authtoken.auth_url)
    #    
    #
    #def _get_roles(self, user_id, tenant_id):
    #    ksclient = self._get_ksclient()
    #    return ksclient.roles.roles_for_user(user_id, tenant_id)
    #
    #def _get_tenants_list(self, user_id):
    #    ksclient = self._get_ksclient()
    #    return ksclient.tenants.get_user_tenants(user_id)


    def _get_query_params(self, req):
        """
        Extracts necessary query params from request.

        :param req: the WSGI Request object
        :retval dict of parameters that can be used by registry client
        """
        params = {'filters': self._get_filters(req)}

        return params

    def _get_filters(self, req):
        """
        Return a dictionary of query param filters from the request

        :param req: the Request object coming from the wsgi layer
        :retval a dict of key/value filters
        """
        query_filters = {}
        for param in req.params:
            query_filters[param] = req.params.get(param)
            if not filters.validate(param, query_filters[param]):
                raise HTTPBadRequest(_('Bad value passed to filter '
                                        '%(filter)s got %(val)s')
                                      % {'filter': param,
                                         'val': query_filters[param]})
        return query_filters

    
    
