# vim: tabstop=4 shiftwidth=4 softtabstop=4
# -*- coding: utf-8 -*-

from __future__ import print_function

import gc
import pprint
import sys
import traceback

import eventlet
import eventlet.backdoor
import greenlet
from cdsoss.common import cfg

eventlet_backdoor_opts = [
    cfg.IntOpt('backdoor_port',
               default=None,
               help='port for eventlet backdoor to listen')
]

CONF = cfg.CONF
CONF.register_opts(eventlet_backdoor_opts)


def _dont_use_this():
    print("Don't use this, just disconnect instead")


def _find_objects(t):
    return filter(lambda o: isinstance(o, t), gc.get_objects())


def _print_greenthreads():
    for i, gt in enumerate(_find_objects(greenlet.greenlet)):
        print(i, gt)
        traceback.print_stack(gt.gr_frame)
        print()


def _print_nativethreads():
    for threadId, stack in sys._current_frames().items():
        print(threadId)
        traceback.print_stack(stack)
        print()


def initialize_if_enabled():
    backdoor_locals = {
        'exit': _dont_use_this,      # So we don't exit the entire process
        'quit': _dont_use_this,      # So we don't exit the entire process
        'fo': _find_objects,
        'pgt': _print_greenthreads,
        'pnt': _print_nativethreads,
    }

    if CONF.backdoor_port is None:
        return None

    # NOTE(johannes): The standard sys.displayhook will print the value of
    # the last expression and set it to __builtin__._, which overwrites
    # the __builtin__._ that gettext sets. Let's switch to using pprint
    # since it won't interact poorly with gettext, and it's easier to
    # read the output too.
    def displayhook(val):
        if val is not None:
            pprint.pprint(val)
    sys.displayhook = displayhook

    sock = eventlet.listen(('localhost', CONF.backdoor_port))
    port = sock.getsockname()[1]
    eventlet.spawn_n(eventlet.backdoor.backdoor_server, sock,
                     locals=backdoor_locals)
    return port
