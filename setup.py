#!/usr/bin/env python
from setuptools import setup, Extension

YAJL_SOURCE_DIR = 'flojay/lloyd-yajl/src'

def yajl_sources():
    source_files = (
        'yajl.c',
        'yajl_gen.c',
        'yajl_alloc.c',
        'yajl_lex.c',
        'yajl_tree.c',
        'yajl_encode.c',
        'yajl_version.c',
        'yajl_buf.c',
        'yajl_parser.c'
    )
    return ['{}/{}'.format(YAJL_SOURCE_DIR, f) for f in source_files]

flojay_extension = Extension(
    'flojay',
    define_macros=[
        ('MAJOR_VERSION', '0'),
        ('MINOR_VERSION', '2')
    ],
    extra_compile_args=['--std=c99'],
    include_dirs=[YAJL_SOURCE_DIR],
    sources=['flojay/flojay.c'] + yajl_sources(),
)

setup(
    name='flojay',
    version='0.2',
    description='Streaming and event-based JSON parser based on yajl',
    author='Robert Church',
    author_email='rchurch@myemma.com',
    url="http://github/myemma/flojay",
    ext_modules=[flojay_extension],
    packages=['flojay'],
    install_requires=['nose==1.1.2'],
    keywords=["json", "stream"],
)
