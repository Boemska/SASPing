#!/usr/bin/env python

from setuptools import setup

setup(
    name='sasping',
    version='0.1',
    author='bojan88',
    url='https://builds.boemskats.com/bojan/sasping',
    packages=['sasping', 'sasping.sas'],
    package_dir={'sasping': '.'},
    include_package_data=True,
    package_data={
        '': ['report/build/index.html']
    }
)
