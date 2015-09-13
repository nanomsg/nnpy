"""Generate the _nnpy.so module from include files"""

from __future__ import print_function
import sys

try:
    from cffi import FFI
except ImportError:
    print("cffi package is needed")
    sys.exit(1)

import os

INCLUDE = ['/usr/include/nanomsg', '/usr/local/include/nanomsg']
BLOCKS = {'{': '}', '(': ')'}

def functions():
    """Get function prototypes from include files"""
    for incdir in INCLUDE:
        if os.path.exists(incdir):
            break

    lines = []
    for incfile in os.listdir(incdir):
        with open(os.path.join(incdir, incfile)) as hincfile:
            cont = ''
            for fileline in hincfile:
                if cont == ',':
                    lines.append(fileline)
                    cont = ''
                if cont in BLOCKS:
                    lines.append(fileline)
                    if BLOCKS[cont] in fileline:
                        cont = ''
                if not (fileline.startswith('NN_EXPORT')
                        or fileline.startswith('typedef')):
                    continue

                lines.append(fileline)
                cont = fileline.strip()[-1]

    return ''.join(fileline[10:] if fileline.startswith('NN_') else fileline for fileline in lines)

def symbols():
    """Get defines from library"""
    nanomsg = ffi.dlopen('nanomsg')

    lines = []
    for i in range(1024):
        val = ffi.new('int*')
        name = nanomsg.nn_symbol(i, val)
        if name == ffi.NULL:
            break

        name = ffi.string(name).decode()
        name = name[3:] if name.startswith('NN_') else name
        lines.append('%s = %s' % (name, val[0]))

    return '\n'.join(lines) + '\n'

# pylint: disable=invalid-name
ffi = FFI()

ffi.set_source("_nnpy",
               """#include <nn.h>
#include <bus.h>
#include <inproc.h>
#include <ipc.h>
#include <pair.h>
#include <pipeline.h>
#include <pubsub.h>
#include <reqrep.h>
#include <survey.h>
#include <tcp.h>""",
               libraries=['nanomsg'],
               include_dirs=['/usr/include/nanomsg', '/usr/local/include/nanomsg'])

ffi.cdef(functions())

with open('nnpy/constants.py', 'w') as handle:
    handle.write(symbols())

if __name__ == '__main__':
    ffi.compile()
