"""NNPY main"""

from .constants import *
from cffi import FFI
import os

HERE = os.path.dirname(__file__)

ffi = FFI()
with open(os.path.join(HERE, 'nanomsg.h')) as f:
    ffi.cdef(f.read())

nanomsg = ffi.dlopen('nanomsg')

from .socket import Socket
