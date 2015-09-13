"""NNPY main"""

from .constants import *
from _nnpy import ffi, lib as nanomsg
import os

from .socket import Socket
