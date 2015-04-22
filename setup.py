from setuptools import setup
import generate

generate.run()

setup(
    name='nnpy',
    version='0.1',
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
    ],
    packages=['nnpy'],
    package_data={'nnpy': ['*.h']},
    install_requires=['cffi'],
)
