from __future__ import print_function
import nnpy

pub = nnpy.Socket(nnpy.AF_SP, nnpy.PUB)
pub.bind('inproc://foo')
print(pub.getsockopt(nnpy.SOL_SOCKET, nnpy.DOMAIN))

sub = nnpy.Socket(nnpy.AF_SP, nnpy.SUB)
sub.connect('inproc://foo')
sub.setsockopt(nnpy.SUB, nnpy.SUB_SUBSCRIBE, b'')

pub.send(b'FLUB')
print(sub.recv())
