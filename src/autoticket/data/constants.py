
class ConstMeta(type):
    def __setattr__(cls, key, value):
        raise AttributeError(
            f"Constants are read-only: cannot set {cls.__name__}.{key} = {value!r}"
        )
