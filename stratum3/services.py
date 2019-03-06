import re
import weakref

from twisted.internet import defer
from twisted.python import log

from stratum3 import exceptions


VENDOR_RE = re.compile(r'\[(.*)\]')


class ResultObject(object):
    def __init__(self, result=None, sign=False, sign_algo=None, sign_id=None):
        self.result = result
        self.sign = sign
        self.sign_algo = sign_algo
        self.sign_id = sign_id


def wrap_result_object(obj):
    def _wrap(o):
        if isinstance(o, ResultObject):
            return o
        return ResultObject(result=o)

    if isinstance(obj, defer.Deferred):
        # We don't have result yet, just wait for it and wrap it later
        obj.addCallback(_wrap)
        return obj

    return _wrap(obj)


class ServiceEventHandler(object): # reimplements event_handler.GenericEventHandler
    def _handle_event(self, msg_method, msg_params, connection_ref):
        return ServiceFactory.call(msg_method, msg_params, connection_ref=connection_ref)


class ServiceFactory(object):
    registry = {}  # Mapping service_type -> vendor -> cls

    @classmethod
    def _split_method(cls, method):
        '''Parses "some.service[vendor].method" string
        and returns 3-tuple with (service_type, vendor, rpc_method)'''

        # Splits the service type and method name
        service_type, method_name = method.rsplit('.', 1)
        vendor = None

        if '[' in service_type:
            # Use regular expression only when brackets found
            try:
                vendor = VENDOR_RE.search(service_type).group(1)
                service_type = service_type.replace('[%s]' % vendor, '')
            except:
                raise

        return service_type, vendor, method_name

    @classmethod
    def call(cls, method, params, connection_ref=None):
        try:
            (service_type, vendor, func_name) = cls._split_method(method)
        except ValueError:
            raise exceptions.MethodNotFoundException(
                "Method name parsing failed. You *must* use format "
                "<service name>.<method name>, e.g. 'example.ping'")

        try:
            if func_name.startswith('_'):
                raise Exception()

            _inst = cls.lookup(service_type, vendor=vendor)()
            _inst.connection_ref = weakref.ref(connection_ref)
            func = _inst.__getattribute__(func_name)
            if not callable(func):
                raise Exception()
        except:
            raise exceptions.MethodNotFoundException(
                "Method '%s' not found for service '%s'" % (func_name, service_type))

        def _run(_func, *params):
            return wrap_result_object(_func(*params))

        # Returns Defer which will lead to ResultObject sometimes
        return defer.maybeDeferred(_run, func, *params)

    @classmethod
    def lookup(cls, service_type, vendor=None):
        # Lookup for service type provided by specific vendor
        if vendor:
            try:
                return cls.registry[service_type][vendor]
            except KeyError:
                raise exceptions.ServiceNotFoundException(
                    "Class for given service type and vendor isn't registered")

        # Lookup for any vendor, prefer default one
        try:
            vendors = cls.registry[service_type]
        except KeyError:
            raise exceptions.ServiceNotFoundException(
                "Class for given service type isn't registered")

        last_found = None
        for _, _cls in vendors.items():
            last_found = _cls
            if last_found.is_default:
                return last_found

        if not last_found:
            raise exceptions.ServiceNotFoundException(
                "Class for given service type isn't registered")

        return last_found

    @classmethod
    def register_service(cls, _cls, meta):
        # Register service class to ServiceFactory
        service_type = meta.get('service_type')
        service_vendor = meta.get('service_vendor')
        is_default = meta.get('is_default')

        if str(_cls.__name__) in ('GenericService',):
            # str() is ugly hack, but it is avoiding circular references
            return

        if not service_type:
            raise exceptions.MissingServiceTypeException(
                "Service class '%s' is missing 'service_type' property." % _cls)

        if not service_vendor:
            raise exceptions.MissingServiceVendorException(
                "Service class '%s' is missing 'service_vendor' property." % _cls)

        if is_default is None:
            raise exceptions.MissingServiceIsDefaultException(
                "Service class '%s' is missing 'is_default' property." % _cls)

        if is_default:
            # Check if there's not any other default service

            try:
                current = cls.lookup(service_type)
                if current.is_default:
                    raise exceptions.DefaultServiceAlreadyExistException(
                        "Default service already exists for type '%s'" % service_type)
            except exceptions.ServiceNotFoundException:
                pass

        setup_func = meta.get('_setup', None)
        if setup_func is not None:
            _cls()._setup()

        ServiceFactory.registry.setdefault(service_type, {})
        ServiceFactory.registry[service_type][service_vendor] = _cls

        log.msg("Registered %s for service '%s', vendor '%s' (default: %s)" %
                (_cls, service_type, service_vendor, is_default))
