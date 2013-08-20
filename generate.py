from cffi import FFI
import os

def functions(dir):
	
	lines = []
	for fn in os.listdir(dir):
		with open(os.path.join(dir, fn)) as f:
			cont = False
			for ln in f:
				
				if cont:
					lines.append(ln)
					cont = False
				if not ln.startswith('NN_EXPORT'):
					continue
				
				lines.append(ln)
				if ln.strip()[-1] != ';':
					cont = True
	
	return ''.join(ln[10:] if ln.startswith('NN_') else ln for ln in lines)

def symbols(headers):
	
	ffi = FFI()
	ffi.cdef(headers)
	nanomsg = ffi.dlopen('nanomsg')
	
	lines = []
	for i in range(1024):
		
		val = ffi.new('int*')
		name = nanomsg.nn_symbol(i, val)
		if name == ffi.NULL:
			break
		
		name = ffi.string(name)
		name = name[3:] if name.startswith('NN_') else name
		lines.append('%s = %s' % (name, val[0]))
	
	return '\n'.join(lines) + '\n'

if __name__ == '__main__':
	
	headers = functions('/usr/include/nanomsg')
	with open('nnpy/nanomsg.h', 'w') as f:
		f.write(headers)
	
	with open('nnpy/constants.py', 'w') as f:
		f.write(symbols(headers))
