# -*- coding: utf-8 -*-

"""cdsoss exception subclasses"""

import six
import six.moves.urllib.parse as urlparse
from cdsoss.common.gettextutils import _

_FATAL_EXCEPTION_FORMAT_ERRORS = False


class RedirectException(Exception):
    def __init__(self, url):
        self.url = urlparse.urlparse(url)


class OssException(Exception):
    """
    Base ops-adapter Exception

    To correctly use this class, inherit from it and define
    a 'message' property. That message will get printf'd
    with the keyword arguments provided to the constructor.
    """
    message = _("An unknown exception occurred")

    def __init__(self, message=None, *args, **kwargs):
        if not message:
            message = self.message
        try:
            if kwargs:
                message = message % kwargs
        except Exception:
            if _FATAL_EXCEPTION_FORMAT_ERRORS:
                raise
            else:
                # at least get the core message out if something happened
                pass
        self.msg = message
        super(OssException, self).__init__(message)

    def __unicode__(self):
        # NOTE(flwang): By default, self.msg is an instance of Message, which
        # can't be converted by str(). Based on the definition of
        # __unicode__, it should return unicode always.
        return six.text_type(self.msg)


class MissingCredentialError(OssException):
    message = _("Missing required credential: %(required)s")


class BadAuthStrategy(OssException):
    message = _("Incorrect auth strategy, expected \"%(expected)s\" but "
                "received \"%(received)s\"")


class NotFound(OssException):
    message = _("An object with the specified identifier was not found.")


class UnknownScheme(OssException):
    message = _("Unknown scheme '%(scheme)s' found in URI")


class Duplicate(OssException):
    message = _("An object with the same identifier already exists.")


class Conflict(OssException):
    message = _("An object with the same identifier is currently being "
                "operated on.")

class NotAvailable(OssException):
    message = _("No available version of service.")

class StorageFull(OssException):
    message = _("There is not enough disk space on the image storage media.")


class StorageQuotaFull(OssException):
    message = _("The size of the data %(image_size)s will exceed the limit. "
                "%(remaining)s bytes remaining.")


class StorageWriteDenied(OssException):
    message = _("Permission to write image storage media denied.")


class AuthBadRequest(OssException):
    message = _("Connect error/bad request to Auth service at URL %(url)s.")


class AuthUrlNotFound(OssException):
    message = _("Auth service at URL %(url)s not found.")


class AuthorizationFailure(OssException):
    message = _("Authorization failed.")


class NotAuthenticated(OssException):
    message = _("You are not authenticated.")


class Forbidden(OssException):
    message = _("You are not authorized to complete this action.")


class Invalid(OssException):
    message = _("Data supplied was not valid.")


class InvalidSortKey(Invalid):
    message = _("Sort key supplied was not valid.")


class InvalidPropertyProtectionConfiguration(Invalid):
    message = _("Invalid configuration in property protection file.")


class InvalidFilterRangeValue(Invalid):
    message = _("Unable to filter using the specified range.")


class ReadonlyProperty(Forbidden):
    message = _("Attribute '%(property)s' is read-only.")


class ReservedProperty(Forbidden):
    message = _("Attribute '%(property)s' is reserved.")


class AuthorizationRedirect(OssException):
    message = _("Redirecting to %(uri)s for authorization.")


class ClientConnectionError(OssException):
    message = _("There was an error connecting to a server")


class ClientConfigurationError(OssException):
    message = _("There was an error configuring the client.")


class MultipleChoices(OssException):
    message = _("The request returned a 302 Multiple Choices. This generally "
                "means that you have not included a version indicator in a "
                "request URI.\n\nThe body of response returned:\n%(body)s")


class LimitExceeded(OssException):
    message = _("The request returned a 413 Request Entity Too Large. This "
                "generally means that rate limiting or a quota threshold was "
                "breached.\n\nThe response body:\n%(body)s")

    def __init__(self, *args, **kwargs):
        self.retry_after = (int(kwargs['retry']) if kwargs.get('retry')
                            else None)
        super(LimitExceeded, self).__init__(*args, **kwargs)


class ServiceUnavailable(OssException):
    message = _("The request returned 503 Service Unavilable. This "
                "generally occurs on service overload or other transient "
                "outage.")

    def __init__(self, *args, **kwargs):
        self.retry_after = (int(kwargs['retry']) if kwargs.get('retry')
                            else None)
        super(ServiceUnavailable, self).__init__(*args, **kwargs)


class ServerError(OssException):
    message = _("The request returned 500 Internal Server Error.")


class UnexpectedStatus(OssException):
    message = _("The request returned an unexpected status: %(status)s."
                "\n\nThe response body:\n%(body)s")


class InvalidContentType(OssException):
    message = _("Invalid content type %(content_type)s")


class BadRegistryConnectionConfiguration(OssException):
    message = _("Registry was not configured correctly on API server. "
                "Reason: %(reason)s")


class BadStoreConfiguration(OssException):
    message = _("Store %(store_name)s could not be configured correctly. "
                "Reason: %(reason)s")


class BadDriverConfiguration(OssException):
    message = _("Driver %(driver_name)s could not be configured correctly. "
                "Reason: %(reason)s")


class MaxRedirectsExceeded(OssException):
    message = _("Maximum redirects (%(redirects)s) was exceeded.")


class InvalidRedirect(OssException):
    message = _("Received invalid HTTP redirect.")


class NoServiceEndpoint(OssException):
    message = _("Response from Keystone does not contain a endpoint.")


class RegionAmbiguity(OssException):
    message = _("Multiple 'image' service matches for region %(region)s. This "
                "generally means that a region is required and you have not "
                "supplied one.")


class WorkerCreationFailure(OssException):
    message = _("Server worker creation failed: %(reason)s.")


class SchemaLoadError(OssException):
    message = _("Unable to load schema: %(reason)s")


class InvalidObject(OssException):
    message = _("Provided object does not match schema "
                "'%(schema)s': %(reason)s")


class UnsupportedHeaderFeature(OssException):
    message = _("Provided header feature is unsupported: %(feature)s")


class RPCError(OssException):
    message = _("%(cls)s exception was raised in the last rpc call: %(val)s")


class DuplicateLocation(Duplicate):
    message = _("The location %(location)s already exists")


class InvalidParameterValue(Invalid):
    message = _("Invalid value '%(value)s' for parameter '%(param)s': "
                "%(extra_msg)s")


class ConfigurationError(OssException):
    """Exception to be raised when invalid settings have been provided."""
    pass


class ServiceCatalogException(OssException):
    """Raised when a requested service is not available in the
    ``ServiceCatalog`` returned by Keystone.
    """
    def __init__(self, service_name):
        message = 'Invalid service catalog service: %s' % service_name
        super(ServiceCatalogException, self).__init__(message)