from . import errors, ffi, nanomsg
import sys
import collections

NN_MSG = int(ffi.cast("size_t", -1))

ustr = str if sys.version_info[0] > 2 else unicode

MessageControl = collections.namedtuple('MessageControl', ['level', 'type', 'data'])

class Socket(object):
    """
    Nanomsg scalability protocols (SP) socket.

    .. seealso:: `nanomsg <http://nanomsg.org/v1.0.0/nanomsg.7.html>`_
    """
    def __init__(self, domain, protocol):
        """
        Create SP socket.

        :param domain: Socket domain `AF_SP` or `AF_SP_RAW`.
        :param protocol: Type of the socket determining its exact
            semantics.

        .. seealso:: `nn_socket <http://nanomsg.org/v1.0.0/nn_socket.3.html>`_
        """
        self.sock = nanomsg.nn_socket(domain, protocol)
    
    def close(self):
        rc = nanomsg.nn_close(self.sock)
        return errors.convert(rc, rc)
    
    def shutdown(self, who):
        rc = nanomsg.nn_shutdown(self.sock, who)
        return errors.convert(rc, rc)
        
    def getsockopt(self, level, option):
        buf = ffi.new('int*')
        size = ffi.new('size_t*')
        size[0] = 4
        rc = nanomsg.nn_getsockopt(self.sock, level, option, buf, size)
        return errors.convert(rc, lambda: buf[0])
    
    def setsockopt(self, level, option, value):
        if isinstance(value, int):
            buf = ffi.new('int*')
            buf[0] = value
            vlen = 4
        elif isinstance(value, ustr):
            buf = ffi.new('char[%s]' % len(value), value.encode())
            vlen = len(value)
        elif isinstance(value, bytes):
            buf = ffi.new('char[%s]' % len(value), value)
            vlen = len(value)
        else:
            raise TypeError("value must be a int, str or bytes")
        rc = nanomsg.nn_setsockopt(self.sock, level, option, buf, vlen)
        errors.convert(rc)
    
    def bind(self, addr):
        addr = addr.encode() if isinstance(addr, ustr) else addr
        buf = ffi.new('char[]', addr)
        rc = nanomsg.nn_bind(self.sock, buf)
        return errors.convert(rc, rc)
    
    def connect(self, addr):
        addr = addr.encode() if isinstance(addr, ustr) else addr
        buf = ffi.new('char[]', addr)
        rc = nanomsg.nn_connect(self.sock, buf)
        return errors.convert(rc, rc)
    
    def send(self, data, flags=0):
        # Some data types can use a zero-copy buffer creation strategy when
        # paired with new versions of CFFI.  Namely, CFFI 1.8 supports `bytes`
        # types with `from_buffer`, which is about 18% faster.  We try the fast
        # way first and degrade as needed for the platform.
        try:
            buf = ffi.from_buffer(data)
        except TypeError:
            data = data.encode() if isinstance(data, ustr) else data
            buf = ffi.new('char[%i]' % len(data), data)
        rc = nanomsg.nn_send(self.sock, buf, len(data), flags)
        return errors.convert(rc, rc)
    
    def recv(self, flags=0):
        buf = ffi.new('char**')
        rc = nanomsg.nn_recv(self.sock, buf, NN_MSG, flags)
        errors.convert(rc)
        s = ffi.buffer(buf[0], rc)[:]
        nanomsg.nn_freemsg(buf[0])
        return s

    def sendmsg(self, data, control, flags=0):
        # Some data types can use a zero-copy buffer creation strategy when
        # paired with new versions of CFFI.  Namely, CFFI 1.8 supports `bytes`
        # types with `from_buffer`, which is about 18% faster.  We try the fast
        # way first and degrade as needed for the platform.
        hdr = ffi.new('struct nn_msghdr *')

        def gen(control_):
            chdr = ffi.new('struct nn_cmsghdr *')
            for level, tp, data in control_:
                chdr.cmsg_level = level
                chdr.cmsg_type = tp
                chdr.cmsg_len = nanomsg.NN_CMSG_SPACE(len(data))
                payload = ffi.buffer(chdr)[:] + data
                padding = b'\0' * (chdr.cmsg_len - len(payload))
                yield payload + padding

        control = b''.join(gen(control))

        try:
            control = ffi.from_buffer(control)
            data = ffi.from_buffer(data)
        except TypeError:
            control = ffi.new('char[%i]' % len(control), control)
            data = data.encode() if isinstance(data, ustr) else data
            data = ffi,new('char[%i]' % len(data), data)
        iov = ffi.new('struct nn_iovec *')
        iov.iov_base = data
        iov.iov_len = len(data)
        hdr.msg_iov = iov
        hdr.msg_iovlen = 1
        hdr.msg_control = control
        hdr.msg_controllen = len(control)

        rc = nanomsg.nn_sendmsg(self.sock, hdr, flags)
        return errors.convert(rc, rc)

    def recvmsg(self, flags=0):
        hdr = ffi.new('struct nn_msghdr *')
        iov = ffi.new('struct nn_iovec *')
        buf = ffi.new('char**')
        control = ffi.new('char **')
        iov.iov_base = buf
        iov.iov_len = NN_MSG
        hdr.msg_iov = iov
        hdr.msg_iovlen = 1
        hdr.msg_control = control
        hdr.msg_controllen = NN_MSG
        rc = nanomsg.nn_recvmsg(self.sock, hdr, flags)
        errors.convert(rc)

        def gen(hdr_):
            chdr = nanomsg.NN_CMSG_FIRSTHDR(hdr_)
            while chdr:
                yield MessageControl(
                        chdr.cmsg_level, chdr.cmsg_type,
                        ffi.buffer(nanomsg.NN_CMSG_DATA(chdr), chdr.cmsg_len - ffi.sizeof(chdr[0]))[:])
                chdr = nanomsg.NN_CMSG_NXTHDR(hdr_, chdr)

        s = ffi.buffer(buf[0], rc)[:]
        c = list(gen(hdr))
        nanomsg.nn_freemsg(buf[0])
        nanomsg.nn_freemsg(control[0])
        return s, c
        
    def get_statistic(self, statistic):
        rc = nanomsg.nn_get_statistic(self.sock, statistic)
        return errors.convert(rc, rc)
