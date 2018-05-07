# -*- coding: utf-8 -*-

from cdsoss.common import wsgi
from cdsoss.api.v1 import regions


class API(wsgi.Router):

    """WSGI router for cdsoss v1 API requests."""

    def __init__(self, mapper):
        regions_resource = regions.create_resource()
        
        mapper.connect("/regions",
                       controller=regions_resource,
                       action='create',
                       conditions={'method': ['POST']})
        mapper.connect("/regions/{id}",
                       controller=regions_resource,
                       action='update',
                       conditions={'method': ['PUT']})
        mapper.connect("/regions",
                       controller=regions_resource,
                       action='index',
                       conditions={'method': ['GET']})
        mapper.connect("/regions/{id}",
                       controller=regions_resource,
                       action='show',
                       conditions={'method': ['GET']})
        mapper.connect("/regions/{id}",
                       controller=regions_resource,
                       action='delete',
                       conditions={'method': ['DELETE']})
        

        super(API, self).__init__(mapper)
