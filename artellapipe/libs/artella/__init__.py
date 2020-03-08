#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Initialization module for artellapipe-libs-artella
"""

import os
import re
import traceback

global artella


class AbstractArtella(object):
    """
    Class that is used by non supported Artella DCCs (such as Houdini) to interface
    with official Artella python module
    """

    @staticmethod
    def getCmsUri(broken_path):
        path_parts = re.split(r'[/\\]', broken_path)
        while len(path_parts):
            path_part = path_parts.pop(0)
            if path_part == '_art':
                relative_path = '/'.join(path_parts)
                return relative_path
        return ''


def init():
    """
    Initializes module
    """

    import tpDcc as tp
    from artellapipe.libs.artella.core import artellalib

    global artella

    if tp.is_maya():
        try:
            import Artella as artella
        except ImportError:
            try:
                artellalib.update_artella_paths()
                if not os.environ.get('ENABLE_ARTELLA_PLUGIN', False):
                    if tp.Dcc.is_plugin_loaded('Artella.py'):
                        tp.Dcc.unload_plugin('Artella.py')
                else:
                    artellalib.load_artella_maya_plugin()
                import Artella as artella
            except Exception as exc:
                artella = AbstractArtella
                print('ERROR: Impossible to load Artella Plugin: {} | {}'.format(exc, traceback.format_exc()))
    else:
        artella = AbstractArtella
        print('Using Abstract Artella Class')
