from __future__ import unicode_literals

import re

from setuptools import find_packages, setup


def get_version(filename):
    content = open(filename).read()
    metadata = dict(re.findall("__([a-z]+)__ = '([^']+)'", content))
    return metadata['version']


setup(
    name='Mopidy-SevenSegmentDisplay',
    version=get_version('mopidy_sevensegmentdisplay/__init__.py'),
    url='https://github.com/JumalIO/mopidy-sevensegmentdisplay',
    license='Apache License, Version 2.0',
    author='Julius',
    author_email='spamjulius@mail.com',
    maintainer='Julius',
    maintainer_email='spamjulius@mail.com',
    description='A Mopidy extension for using it with seven segment display.',
    long_description=open('README.rst').read(),
    packages=find_packages(exclude=['tests', 'tests.*']),
    zip_safe=False,
    include_package_data=True,
    install_requires=[
        'setuptools',
        'Mopidy >= 0.19',
        'Pykka >= 1.1',
        'monotonic >= 1.4',
        'python-lirc',
    ],
    test_suite='nose.collector',
    tests_require=[
        'nose',
        'mock >= 1.0',
    ],
    entry_points={
        'mopidy.ext': [
            'sevensegmentdisplay = mopidy_sevensegmentdisplay:Extension',
        ],
    },
    classifiers=[
        'Environment :: No Input/Output (Daemon)',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Topic :: Multimedia :: Sound/Audio :: Players',
    ],
)
