# -*- coding: utf-8 -*-

from webob.exc import HTTPBadRequest
from webob.exc import HTTPConflict
from webob.exc import HTTPForbidden
from webob.exc import HTTPNotFound
from webob.exc import HTTPRequestEntityTooLarge
from webob import Response

from cdsoss.common import exception

from cdsoss.common import wsgi
import cdsoss.common.log as logging
from cdsoss.api.v1 import controller

from cdsoss.manage.namespace import region as region_manage

LOG = logging.getLogger(__name__)


class Controller(controller.BaseController):

    def index(self, req):
        regions = region_manage.list_region() 
        return {'regions': regions}
    
    def show(self, req, id):
        region = {}
        try:
            region = region_manage.get_region(id)
        except exception.NotFound as e:
            msg = _("Failed to get region: %(e)s") % {'e': e}
            LOG.error(msg)
            raise HTTPNotFound(explanation=msg,
                               request=req,
                               content_type="text/plain")   
        return {'region': region}
    
    @controller.para_check(outer_key='region',
                           must_key=['name', 'mgmt_ip',
                                     'mgmt_port', 'mgmt_user',
                                     'mgmt_passwd'])
    def create(self, req, body):
        values = body.get('region',{})
        region = {}
        try:
            region = region_manage.create_region(values)
        except Exception as e:
            LOG.error(e)
            raise HTTPBadRequest(explanation=_("Error: %s") % e,
                     request=req,
                     content_type="text/plain")
        return Response(body=str(region), status=201)
    
    @controller.para_check(outer_key='region',
                           mustnot_key=['name', 'mgmt_ip',
                                        'mgmt_port', 'mgmt_user',
                                        'mgmt_passwd', 'enable'])
    def update(self, req, id, body):
        values = body.get('region',{})
        region = {}
        try:
            region = region_manage.update_region(id, values)
        except Exception as e:
            LOG.error(e)
            raise HTTPBadRequest(explanation=_("Error: %s") % e,
                     request=req,
                     content_type="text/plain")
        
        return Response(status=204)
    
    def delete(self, req, id):
        try:
            region = region_manage.delete_region(id)
        except exception.NotFound as e:
            msg = _("Failed to delete region: %(e)s") % {'e': e}
            LOG.error(msg)
            raise HTTPNotFound(explanation=msg,
                               request=req,
                               content_type="text/plain")
        except exception.Conflict as e:
            msg = _("Failed to delete region: %(e)s") % {'e': e}
            LOG.error(msg)
            raise HTTPConflict(explanation=msg,
                               request=req,
                               content_type="text/plain")
        
        return Response(status=204)


def create_resource():
    deserializer = wsgi.JSONRequestDeserializer()
    serializer = wsgi.JSONResponseSerializer()
    return wsgi.Resource(Controller(), deserializer, serializer)