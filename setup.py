# -*- coding: utf-8 -*-

try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup

with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name = 'Ship-Shape-File-Navigator',
    
    version = '0.1',
    
    url = 'http://www.shipshapefilenavigator.org',

    description = 'A shipshape Shapefile File Navigator',
    long_description = readme,
    download_url = 'https://bitbucket.org/shipshp/shipshpfn/downloads',
    
    author = 'Adrián Eirís Torres',
    author_email = 'adrianet82[at]gmail.com',

    license = license,
    
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Developers',
        'Topic :: Scientific/Engineering :: GIS',
        'Topic :: Desktop Environment :: File Managers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: POSIX :: Linux',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 2 :: Only',
    ],
    
    keywords = 'gis shapefile file navigator',
    
    packages = ['shipshpfn', 'shipshpfn.lib', 'shipshpfn.tools']
    #~ packages = find_packages(exclude=['data-samples', 'docs', 'tests'])
)
