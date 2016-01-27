from cffi import FFI
import os

INCLUDE = ['/usr/include/nanomsg', '/usr/local/include/nanomsg']
if 'CPATH' in os.environ:
    INCLUDE += [os.path.join(p, 'nanomsg') for p in os.getenv('CPATH').split(os.pathsep)]
BLOCKS = {'{': '}', '(': ')'}

def header_files():
    for dir in INCLUDE:
        if os.path.exists(dir):
            break
    return {fn: os.path.join(dir, fn) for fn in os.listdir(dir)}

def functions(hfiles):
    
    lines = []
    for fn, path in hfiles.items():
        with open(path) as f:
            cont = ''
            for ln in f:
                
                if cont == ',':
                    lines.append(ln)
                    cont = ''
                if cont in BLOCKS:
                    lines.append(ln)
                    if BLOCKS[cont] in ln:
                        cont = ''
                if not (ln.startswith('NN_EXPORT')
                    or ln.startswith('typedef')):
                    continue
                
                lines.append(ln)
                cont = ln.strip()[-1]
    
    return ''.join(ln[10:] if ln.startswith('NN_') else ln for ln in lines)

def symbols(ffi):
    
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

def create_module():

    hfiles = header_files()
    # remove ws.h due to https://github.com/nanomsg/nanomsg/issues/467
    hfiles.pop('ws.h', None)

    ffi = FFI()
    ffi.cdef(functions(hfiles))
    ffi.set_source('_nnpy', '\n'.join('#include <%s>' % fn for fn in hfiles),
                   libraries=['nanomsg'], include_dirs=INCLUDE)
    return ffi

ffi = create_module()
with open('nnpy/constants.py', 'w') as f:
    f.write(symbols(ffi))

if __name__ == '__main__':
    ffi.compile()
