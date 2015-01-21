#!/usr/bin/env python

import os
import sys
from glob import glob

sys.path.insert(0, os.path.abspath('lib'))
from sojourner import __version__, __author__
try:
    from setuptools import setup, find_packages
except ImportError:
    print "Sojourner now needs setuptools in order to build. " \
          "Install it using your package manager (usually python-setuptools) or via pip (pip install setuptools)."
    sys.exit(1)

setup(name='sojourner',
      version=__version__,
      description='Wrapper For Config Management Tools',
      author=__author__,
      author_email='junaid18183@gmail.com',
      url='https://github.com/junaid18183/Sojourner',
      license='GPLv3',
      install_requires=["argparse", "ConfigParser"],
      package_dir={ 'sojourner': 'lib/sojourner' },
      packages=find_packages('lib'),
      include_package_data=True,
      scripts=[
         'bin/sojourner',
      ],
      data_files=[
                ('/etc/sojourner', ['examples/sojourner.cfg']),
               ],

)
