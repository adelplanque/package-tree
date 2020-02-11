#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from setuptools import setup

setup(
    name                 = 'package-tree',
    version              = '0.1',
    description          = 'Graph of python package dependencies.',
    packages             = ('package_tree', ),
    entry_points         = {
        "console_scripts": [
            "package-tree = package_tree.tree:main",
        ],
    },
)
