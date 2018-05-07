
from cdsoss.common import cfg
import paste.urlmap

CONF = cfg.CONF


def root_app_factory(loader, global_conf, **local_conf):
    if not CONF.enable_v1_api:
        del local_conf['/v1']
    return paste.urlmap.urlmap_factory(loader, global_conf, **local_conf)
