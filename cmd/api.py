# -*- coding: utf-8 -*-
#!/usr/bin/env python

import eventlet
import os
import sys

import six

# Monkey patch socket, time, select, threads
eventlet.patcher.monkey_patch(all=False, socket=True, time=True,
                              select=True, thread=True)

possible_topdir = os.path.normpath(os.path.join(os.path.abspath(sys.argv[0]),
                                   os.pardir,
                                   os.pardir))
if os.path.exists(os.path.join(possible_topdir, 'cdsoss', '__init__.py')):
    sys.path.insert(0, possible_topdir)

from cdsoss.common import config
from cdsoss.common import exception
from cdsoss.common import wsgi
from cdsoss.common import log



def fail(returncode, e):
    sys.stderr.write("ERROR: %s\n" % six.text_type(e))
    sys.exit(returncode)


def main():
    try:
        config.parse_args()
        log.setup('cdsoss')

        server = wsgi.Server()
        server.start(config.load_paste_app('cdsoss-api'), default_port=8491)
        server.wait()
    except exception.WorkerCreationFailure as e:
        fail(2, e)
    except RuntimeError as e:
        fail(1, e)


if __name__ == '__main__':
    main()
