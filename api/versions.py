# -*- coding: utf-8 -*-

import httplib

from cdsoss.common import cfg
import webob.dec

from cdsoss.common import wsgi
from cdsoss.common import jsonutils


CONF = cfg.CONF


class Controller(object):

    """A wsgi controller that reports which API versions are supported."""

    def index(self, req):
        """Respond to a request for all cdsoss API versions."""
        def build_version_object(version, path, status):
            return {
                'id': 'v%s' % version,
                'status': status,
                'links': [
                    {
                        'rel': 'self',
                        'href': '%s/%s/' % (req.host_url, path),
                    },
                ],
            }

        version_objs = []
        if CONF.enable_v1_api:
            version_objs.extend([
                build_version_object(1.0, 'v1', 'CURRENT'),
            ])

        response = webob.Response(request=req,
                                  status=httplib.MULTIPLE_CHOICES,
                                  content_type='application/json')
        response.body = jsonutils.dumps(dict(versions=version_objs))
        return response

    @webob.dec.wsgify(RequestClass=wsgi.Request)
    def __call__(self, req):
        return self.index(req)


def create_resource(conf):
    return wsgi.Resource(Controller())
