from . import nanomsg, ffi
from .constants import *
import sys

class Socket(object):
	
	def __init__(self, domain, protocol):
		self.sock = nanomsg.nn_socket(domain, protocol)
	
	def close(self):
		nanomsg.nn_close(self.sock)
	
	def getsockopt(self, level, option):
		buf = ffi.new('int*')
		size = ffi.new('size_t*')
		size[0] = 4
		rc = nanomsg.nn_getsockopt(self.sock, level, option, buf, size)
		assert rc >= 0, rc
		return buf[0]
	
	def setsockopt(self, level, option, value):
		if isinstance(value, int):
			buf = ffi.new('int*')
			buf[0] = value
			vlen = 4
		elif isinstance(value, (str, bytes)):
			buf = ffi.new('char[%s]' % len(value), value)
			vlen = len(value)
		else:
			raise TypeError("value must be a int, str or bytes")
		rc = nanomsg.nn_setsockopt(self.sock, level, option, buf, vlen)
		assert rc >= 0, rc
	
	def bind(self, addr):
		buf = ffi.new('char[]', addr.encode())
		rc = nanomsg.nn_bind(self.sock, buf)
		assert rc > 0, rc
	
	def connect(self, addr):
		buf = ffi.new('char[]', addr.encode())
		rc = nanomsg.nn_connect(self.sock, buf)
		assert rc > 0, rc
	
	def send(self, data, flags=0):
		l = len(data)
		buf = ffi.new('char[%i]' % l, data)
		rc = nanomsg.nn_send(self.sock, buf, l, flags)
		assert rc > 0, rc
	
	def recv(self, flags=0):
		buf = ffi.new('char**')
		rc = nanomsg.nn_recv(self.sock, buf, sys.maxsize * 2 - 1, flags)
		assert rc > 0, rc
		return ffi.buffer(buf, rc)[:]
