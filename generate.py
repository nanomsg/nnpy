from cffi import FFI
import os

INCLUDE = ['/usr/include/nanomsg', '/usr/local/include/nanomsg']
BLOCKS = {'{': '}', '(': ')'}

def functions():
	
	for dir in INCLUDE:
		if os.path.exists(dir):
			break
	
	lines = []
	for fn in os.listdir(dir):
		with open(os.path.join(dir, fn)) as f:
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
		
		name = ffi.string(name).decode()
		name = name[3:] if name.startswith('NN_') else name
		lines.append('%s = %s' % (name, val[0]))
	
	return '\n'.join(lines) + '\n'

def run():
	headers = functions()
	with open('nnpy/nanomsg.h', 'w') as f:
		f.write(headers)
	with open('nnpy/constants.py', 'w') as f:
		f.write(symbols(headers))

if __name__ == '__main__':
	run()
