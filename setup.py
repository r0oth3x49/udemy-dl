#!/usr/bin/env python
# -*- coding: utf-8 -*-
 
import os
import shutil
from setuptools import setup, find_packages

if not os.path.exists('scripts'):
    os.makedirs('scripts')
if not os.path.exists('scripts/udemy-dl'):
    shutil.copyfile('udemy-dl.py', 'scripts/udemy-dl')

setup(
    name='udemy-dl',
    version="0.5",
    description='download umdemy course',
    license='License :: OSI Approved :: MIT License',
    platforms='Platform Independent',
    author="r0oth3x49",
    url='https://github.com/r0oth3x49/udemy-dl',
    install_requires = [
        'requests[security]', 'six', 'colorama',
        'requests', 'unidecode', 'pyOpenSSL',
    ],
    packages=find_packages(),
    scripts=['scripts/udemy-dl'],
    keywords=['udemy', 'download'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ]
)
