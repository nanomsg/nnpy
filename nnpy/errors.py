from _nnpy import ffi, lib as nanomsg

class NNError(Exception):
    pass

def convert(rc, value=None):
    if rc < 0:
        chars = nanomsg.nn_strerror(nanomsg.nn_errno())
        raise NNError(ffi.string(chars))
    if callable(value):
        return value()
    return value

