from setuptools import setup

setup(
    name='nnpy',
    version='0.9.1',
    url='https://github.com/nanomsg/nnpy',
    license='MIT',
    author='Dirkjan Ochtman',
    author_email='dirkjan@ochtman.nl',
    description='cffi-based Python bindings for nanomsg',
    long_description=open('README.rst').read(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: Implementation :: CPython',
    ],
    packages=['nnpy'],
    setup_requires=["cffi>=1.0.0"],
    cffi_modules=["generate.py:ffi"],
    install_requires=['cffi'],
)
