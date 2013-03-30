#!/usr/bin/env python
import os
import crate
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

version = crate.__version__
setup(
    name='crate',
    version=version,
    description='Linux Container Management',
    url='http://github.com/ehazlett/crate',
    download_url=('https://github.com/ehazlett/'
                  'crate/archive/%s.tar.gz' % version),
    author='Evan Hazlett',
    author_email='ejhazlett@gmail.com',
    keywords=['deployment'],
    license='Apache 2.0',
    packages=['crate'],
    entry_points={
        'console_scripts': [
            'crate = crate.runner:main',
        ],
    },
    install_requires = [ 'fabric', ],
    test_suite='tests.all_tests',
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        ]
)
