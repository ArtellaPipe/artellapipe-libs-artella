#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Utility module that contains useful utilities and classes related with Artella
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpovedatd@gmail.com"

import os
import traceback

import tpDcc as tp

import artellapipe
from artellapipe.libs.artella.core import abstract

global artella

# To have auto completion
artella = abstract


class ArtellaProjectType(object):
    INDIE = 'indie'
    ENTERPRISE = 'enterprise'


def init_artella(dev=False):

    global artella

    try:
        from artellapipe.libs.artella.core import artellaenterprise
        artella = artellaenterprise
        artella.init(dev=dev)
        artellapipe.logger.info('Using Artella Enterprise')
    except ImportError:
        from artellapipe.libs.artella.core import artellaindie
        artella = artellaindie
        if tp.is_maya():
            try:
                import Artella as art
            except ImportError:
                try:
                    artellaindie.update_artella_paths()
                    if not os.environ.get('ENABLE_ARTELLA_PLUGIN', False):
                        if tp.Dcc.is_plugin_loaded('Artella.py'):
                            tp.Dcc.unload_plugin('Artella.py')
                    else:
                        artella.load_artella_maya_plugin()
                    import Artella as art
                except Exception as exc:
                    artellapipe.logger.error(
                        'Impossible to load Artella Plugin: {} | {}'.format(exc, traceback.format_exc()))
        else:
            artellapipe.logger.info('Using Abstract Artella Class')
    except Exception as exc:
        artellapipe.logger.error(
            'Artella Enterprise is installed but an error happened while loading it: {} | {}!'.format(
                exc, traceback.format_exc()))
