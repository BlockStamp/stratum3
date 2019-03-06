#!/usr/bin/env python

from setuptools import setup
from stratum3 import version

setup(name='stratum3',
      version=version.VERSION,
      description='Stratum server implementation based on Twisted for python3',
      author='blockstamp',
      author_email='support@blockstamp.info',
      url='https://blockstamp.info',
      packages=['stratum3'],
      zip_safe=False,
      install_requires=['twisted', 'ecdsa', 'autobahn']
     )
