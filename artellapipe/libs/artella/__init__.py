#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Initialization module for artellapipe-libs-artella
"""

from artellapipe.libs.artella.core import artellalib


def init(dev=False):
    """
    Initializes module
    """

    artellalib.init_artella(dev=dev)
