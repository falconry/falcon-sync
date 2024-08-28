import inspect


class ProxyMeta(type):
    _ADAPTER = '_adapter'

    @classmethod
    def create_method(cls, base_name, attr):
        def method(obj, *args, **kwargs):
            original = getattr(obj, base_name)
            return getattr(original, attr)(*args, **kwargs)

        return method

    @classmethod
    def create_ro_property(cls, base_name, attr):
        def fget(obj):
            original = getattr(obj, base_name)
            return getattr(original, attr)

        return property(fget)

    @classmethod
    def create_rw_property(cls, base_name, attr):
        def fget(obj):
            original = getattr(obj, base_name)
            return getattr(original, attr)

        def fset(obj, value):
            original = getattr(obj, base_name)
            setattr(original, attr, value)

        return property(fget, fset)

    def __new__(cls, name, bases, dct):
        proxy_cls = super().__new__(cls, name, bases, dct)

        (base_cls,) = bases
        base_name = f'_{base_cls.__name__.lower()}'

        for attr, member in inspect.getmembers(proxy_cls):
            if attr.startswith('_'):
                continue
            if attr in dct:
                continue
            if attr in proxy_cls._PROXY_INHERIT:
                continue

            if inspect.isfunction(member):
                setattr(proxy_cls, attr, cls.create_method(base_name, attr))

            elif isinstance(member, property):
                if member.fset is None:
                    prop = cls.create_ro_property(base_name, attr)
                else:
                    prop = cls.create_rw_property(base_name, attr)
                setattr(proxy_cls, attr, prop)

            else:
                setattr(
                    proxy_cls, attr, cls.create_rw_property(base_name, attr)
                )

        return proxy_cls
