#!/usr/bin/env python
from setuptools import setup, Extension
from distutils.core import setup
import os
from flojay import __version__

yajl_sources = ['flojay/lloyd-yajl/src/' + file_ for file_ in \
    ('yajl.c', 'yajl_gen.c', 'yajl_alloc.c', 'yajl_lex.c', 'yajl_tree.c', \
     'yajl_encode.c', 'yajl_version.c', 'yajl_buf.c', 'yajl_parser.c')]

major_minor = __version__.split('.')

flojay = Extension('flojay',
                    define_macros=[
                        ('MAJOR_VERSION', major_minor[0]),
                        ('MINOR_VERSION', major_minor[1])],
                    extra_compile_args=['--std=c99'],
                    include_dirs=['flojay/lloyd-yajl/src'],
                    sources=yajl_sources + ['flojay/flojay.c'])


setup(
    name='flojay',
    version=__version__,
    description='Streaming and event-based JSON parser based on yajl',
    author='Robert Church',
    author_email='rchurch@myemma.com',
    url = "http://github/myemma/flojay/",
    ext_modules=[flojay],
    packages=['flojay'],
    install_requires=['nose==1.1.2'],
    keywords = ["json", "stream", "ajax", "webapp", "website", "data", "messaging"],
    classifiers = [
        "Programming Language :: Python",
        "Development Status :: 2 - Pre-Alpha",
        "Environment :: Other Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet",
        ],
    )

