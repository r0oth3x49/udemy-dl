#!/usr/bin/env python3

from setuptools import setup

with open("README.md", "r") as f:
    long_description = f.read()

with open("requirements.txt", "r") as f:
    install_required = f.read().splitlines()

setup(
    name="udemy-dl",
    version="1.1",
    description="A cross-platform python based utility to download courses from udemy for personal offline use.",
    long_description=long_description,
    author="Nasir Khan (r0ot h3x49)",
    license="MIT",
    url="https://github.com/r0oth3x49/udemy-dl",
    install_requires=install_required,
    packages=["udemy", "udemy.colorized"],
    scripts=["udemy-dl"]
)
