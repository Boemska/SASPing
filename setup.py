#!/usr/bin/env python

from distutils.core import setup

setup(
    name='sasping',
    version='0.1',
    author='bojan88',
    url='https://builds.boemskats.com/bojan/sasping',
    packages=['sasping', 'sasping.sas'],
    package_dir={'sasping': '.'},
    data_files=[
      ('report', 'build/index.html')
    ],
)
