# -*- coding: utf-8 -*-

"""
System-level utilities and helper functions.
"""

import errno

try:
    from eventlet import sleep
except ImportError:
    from time import sleep
from eventlet.green import socket

import functools
import os
import platform
import subprocess
import sys
import uuid
import six
import copy

from OpenSSL import crypto
from cdsoss.common import cfg
from webob import exc

from cdsoss.common import exception
import cdsoss.common.log as logging
from cdsoss.common import strutils

CONF = cfg.CONF

LOG = logging.getLogger(__name__)

FEATURE_BLACKLIST = ['content-length', 'content-type', 'x-cdsoss-meta-size']


UNITELOG_TEST_SOCKET_FD_STR = 'UNITELOG_TEST_SOCKET_FD'


def chunkreadable(iter, chunk_size=65536):
    """
    Wrap a readable iterator with a reader yielding chunks of
    a preferred size, otherwise leave iterator unchanged.

    :param iter: an iter which may also be readable
    :param chunk_size: maximum size of chunk
    """
    return chunkiter(iter, chunk_size) if hasattr(iter, 'read') else iter


def chunkiter(fp, chunk_size=65536):
    """
    Return an iterator to a file-like obj which yields fixed size chunks

    :param fp: a file-like object
    :param chunk_size: maximum size of chunk
    """
    while True:
        chunk = fp.read(chunk_size)
        if chunk:
            yield chunk
        else:
            break


def cooperative_iter(iter):
    """
    Return an iterator which schedules after each
    iteration. This can prevent eventlet thread starvation.

    :param iter: an iterator to wrap
    """
    try:
        for chunk in iter:
            sleep(0)
            yield chunk
    except Exception as err:
        msg = _("Error: cooperative_iter exception %s") % err
        LOG.error(msg)
        raise


def cooperative_read(fd):
    """
    Wrap a file descriptor's read with a partial function which schedules
    after each read. This can prevent eventlet thread starvation.

    :param fd: a file descriptor to wrap
    """
    def readfn(*args):
        result = fd.read(*args)
        sleep(0)
        return result
    return readfn


def add_features_to_http_headers(features, headers):
    """
    Adds additional headers representing cdsoss features to be enabled.

    :param headers: Base set of headers
    :param features: Map of enabled features
    """
    if features:
        for k, v in features.items():
            if k.lower() in FEATURE_BLACKLIST:
                raise exception.UnsupportedHeaderFeature(feature=k)
            if v is not None:
                headers[k.lower()] = unicode(v)



def safe_mkdirs(path):
    try:
        os.makedirs(path)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise


def safe_remove(path):
    try:
        os.remove(path)
    except OSError as e:
        if e.errno != errno.ENOENT:
            raise


def get_terminal_size():

    def _get_terminal_size_posix():
        import fcntl
        import struct
        import termios

        height_width = None

        try:
            height_width = struct.unpack('hh', fcntl.ioctl(sys.stderr.fileno(),
                                         termios.TIOCGWINSZ,
                                         struct.pack('HH', 0, 0)))
        except Exception:
            pass

        if not height_width:
            try:
                p = subprocess.Popen(['stty', 'size'],
                                     shell=False,
                                     stdout=subprocess.PIPE,
                                     stderr=open(os.devnull, 'w'))
                result = p.communicate()
                if p.returncode == 0:
                    return tuple(int(x) for x in result[0].split())
            except Exception:
                pass

        return height_width

    def _get_terminal_size_win32():
        try:
            from ctypes import create_string_buffer
            from ctypes import windll
            handle = windll.kernel32.GetStdHandle(-12)
            csbi = create_string_buffer(22)
            res = windll.kernel32.GetConsoleScreenBufferInfo(handle, csbi)
        except Exception:
            return None
        if res:
            import struct
            unpack_tmp = struct.unpack("hhhhHhhhhhh", csbi.raw)
            (bufx, bufy, curx, cury, wattr,
             left, top, right, bottom, maxx, maxy) = unpack_tmp
            height = bottom - top + 1
            width = right - left + 1
            return (height, width)
        else:
            return None

    def _get_terminal_size_unknownOS():
        raise NotImplementedError

    func = {'posix': _get_terminal_size_posix,
            'win32': _get_terminal_size_win32}

    height_width = func.get(platform.os.name, _get_terminal_size_unknownOS)()

    if height_width is None:
        raise exception.Invalid()

    for i in height_width:
        if not isinstance(i, int) or i <= 0:
            raise exception.Invalid()

    return height_width[0], height_width[1]


def mutating(func):
    """Decorator to enforce read-only logic"""
    @functools.wraps(func)
    def wrapped(self, req, *args, **kwargs):
        if req.context.read_only:
            msg = _("Read-only access")
            LOG.debug(msg)
            raise exc.HTTPForbidden(msg, request=req,
                                    content_type="text/plain")
        return func(self, req, *args, **kwargs)
    return wrapped


def setup_remote_pydev_debug(host, port):
    error_msg = ('Error setting up the debug environment.  Verify that the'
                 ' option pydev_worker_debug_port is pointing to a valid '
                 'hostname or IP on which a pydev server is listening on'
                 ' the port indicated by pydev_worker_debug_port.')

    try:
        try:
            from pydev import pydevd
        except ImportError:
            import pydevd

        pydevd.settrace(host,
                        port=port,
                        stdoutToServer=True,
                        stderrToServer=True)
        return True
    except Exception:
        LOG.exception(error_msg)
        raise


class LazyPluggable(object):
    """A pluggable backend loaded lazily based on some value."""

    def __init__(self, pivot, config_group=None, **backends):
        self.__backends = backends
        self.__pivot = pivot
        self.__backend = None
        self.__config_group = config_group

    def __get_backend(self):
        if not self.__backend:
            if self.__config_group is None:
                backend_name = CONF[self.__pivot]
            else:
                backend_name = CONF[self.__config_group][self.__pivot]
            if backend_name not in self.__backends:
                msg = _('Invalid backend: %s') % backend_name
                raise exception.OssException(msg)

            backend = self.__backends[backend_name]
            if isinstance(backend, tuple):
                name = backend[0]
                fromlist = backend[1]
            else:
                name = backend
                fromlist = backend

            self.__backend = __import__(name, None, None, fromlist)
        return self.__backend

    def __getattr__(self, key):
        backend = self.__get_backend()
        return getattr(backend, key)


def validate_key_cert(key_file, cert_file):
    try:
        error_key_name = "private key"
        error_filename = key_file
        key_str = open(key_file, "r").read()
        key = crypto.load_privatekey(crypto.FILETYPE_PEM, key_str)

        error_key_name = "certficate"
        error_filename = cert_file
        cert_str = open(cert_file, "r").read()
        cert = crypto.load_certificate(crypto.FILETYPE_PEM, cert_str)
    except IOError as ioe:
        raise RuntimeError(_("There is a problem with your %(error_key_name)s "
                             "%(error_filename)s.  Please verify it."
                             "  Error: %(ioe)s") %
                           {'error_key_name': error_key_name,
                            'error_filename': error_filename,
                            'ioe': ioe})
    except crypto.Error as ce:
        raise RuntimeError(_("There is a problem with your %(error_key_name)s "
                             "%(error_filename)s.  Please verify it. OpenSSL"
                             " error: %(ce)s") %
                           {'error_key_name': error_key_name,
                            'error_filename': error_filename,
                            'ce': ce})

    try:
        data = str(uuid.uuid4())
        digest = "sha1"

        out = crypto.sign(key, data, digest)
        crypto.verify(cert, out, data, digest)
    except crypto.Error as ce:
        raise RuntimeError(_("There is a problem with your key pair.  "
                             "Please verify that cert %(cert_file)s and "
                             "key %(key_file)s belong together.  OpenSSL "
                             "error %(ce)s") % {'cert_file': cert_file,
                                                'key_file': key_file,
                                                'ce': ce})


def get_test_suite_socket():
    global UNITELOG_TEST_SOCKET_FD_STR
    if UNITELOG_TEST_SOCKET_FD_STR in os.environ:
        fd = int(os.environ[UNITELOG_TEST_SOCKET_FD_STR])
        sock = socket.fromfd(fd, socket.AF_INET, socket.SOCK_STREAM)
        sock = socket.SocketType(_sock=sock)
        sock.listen(CONF.backlog)
        del os.environ[UNITELOG_TEST_SOCKET_FD_STR]
        os.close(fd)
        return sock
    return None


def is_uuid_like(val):
    """Returns validation of a value as a UUID.

    For our purposes, a UUID is a canonical form string:
    aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa
    """
    try:
        return str(uuid.UUID(val)) == val
    except (TypeError, ValueError, AttributeError):
        return False


class SortedDict(dict):
    """
    A dictionary that keeps its keys in the order in which they're inserted.
    """
    def __new__(cls, *args, **kwargs):
        instance = super(SortedDict, cls).__new__(cls, *args, **kwargs)
        instance.keyOrder = []
        return instance

    def __init__(self, data=None):
        if data is None or isinstance(data, dict):
            data = data or []
            super(SortedDict, self).__init__(data)
            self.keyOrder = list(data) if data else []
        else:
            super(SortedDict, self).__init__()
            super_set = super(SortedDict, self).__setitem__
            for key, value in data:
                # Take the ordering from first key
                if key not in self:
                    self.keyOrder.append(key)
                # But override with last value in data (dict() does this)
                super_set(key, value)

    def __deepcopy__(self, memo):
        return self.__class__([(key, copy.deepcopy(value, memo))
                               for key, value in self.items()])

    def __copy__(self):
        # The Python's default copy implementation will alter the state
        # of self. The reason for this seems complex but is likely related to
        # subclassing dict.
        return self.copy()

    def __setitem__(self, key, value):
        if key not in self:
            self.keyOrder.append(key)
        super(SortedDict, self).__setitem__(key, value)

    def __delitem__(self, key):
        super(SortedDict, self).__delitem__(key)
        self.keyOrder.remove(key)

    def __iter__(self):
        return iter(self.keyOrder)

    def __reversed__(self):
        return reversed(self.keyOrder)

    def pop(self, k, *args):
        result = super(SortedDict, self).pop(k, *args)
        try:
            self.keyOrder.remove(k)
        except ValueError:
            # Key wasn't in the dictionary in the first place. No problem.
            pass
        return result

    def popitem(self):
        result = super(SortedDict, self).popitem()
        self.keyOrder.remove(result[0])
        return result

    def _iteritems(self):
        for key in self.keyOrder:
            yield key, self[key]

    def _iterkeys(self):
        for key in self.keyOrder:
            yield key

    def _itervalues(self):
        for key in self.keyOrder:
            yield self[key]

    if six.PY3:
        items = _iteritems
        keys = _iterkeys
        values = _itervalues
    else:
        iteritems = _iteritems
        iterkeys = _iterkeys
        itervalues = _itervalues

        def items(self):
            return [(k, self[k]) for k in self.keyOrder]

        def keys(self):
            return self.keyOrder[:]

        def values(self):
            return [self[k] for k in self.keyOrder]

    def update(self, dict_):
        for k, v in six.iteritems(dict_):
            self[k] = v

    def setdefault(self, key, default):
        if key not in self:
            self.keyOrder.append(key)
        return super(SortedDict, self).setdefault(key, default)

    def copy(self):
        """Returns a copy of this object."""
        # This way of initializing the copy means it works for subclasses, too.
        return self.__class__(self)

    def __repr__(self):
        """
        Replaces the normal dict.__repr__ with a version that returns the keys
        in their sorted order.
        """
        return '{%s}' % ', '.join('%r: %r' % (k, v) for k, v in six.iteritems(self))

    def clear(self):
        super(SortedDict, self).clear()
        self.keyOrder = []