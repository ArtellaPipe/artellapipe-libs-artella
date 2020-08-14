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

from functools import wraps
from importlib import import_module

from tpDcc.libs.python import decorators

import artellapipe


# Caches used to store all the reroute paths done during a session
REROUTE_CACHE = dict()
INDIE_MODULE = None
ENTERPRISE_MODULE = None


class ArtellaProjectType(object):
    INDIE = 'indie'
    ENTERPRISE = 'enterprise'


def init_artella(dev=False, project_type=ArtellaProjectType.ENTERPRISE):

    if project_type == ArtellaProjectType.ENTERPRISE:

        # Import all functions in an explicit way
        from artellapipe.libs.artella.core import artellaenterprise
        artellaenterprise.init(dev=dev)
        artellapipe.logger.info('Using Artella Enterprise')
    else:
        # Import all functions in an explicit way
        from artellapipe.libs.artella.core import artellaindie
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
                        artellaindie.load_artella_maya_plugin()
                    import Artella as art
                except Exception as exc:
                    artellapipe.logger.error(
                        'Impossible to load Artella Plugin: {} | {}'.format(exc, traceback.format_exc()))
        else:
            artellapipe.logger.info('Using Abstract Artella Class')


def reroute(fn):
    """
    Decorator that rerouts the function call on runtime to the specific Artella API function call depending on the
    current project Artella type (Indie or Enterprise)
    :param fn:
    :return:
    """

    @wraps(fn)
    def wrapper(*args, **kwargs):

        global REROUTE_CACHE

        base_module = 'artellapipe.libs.artella.core'

        if artellapipe.project.is_enterprise():

            global ENTERPRISE_MODULE

            if 'enterprise' not in REROUTE_CACHE:
                REROUTE_CACHE['enterprise'] = dict()

            module_name = '{}.artellaenterprise'.format(base_module)
            if not ENTERPRISE_MODULE:
                try:
                    ENTERPRISE_MODULE = import_module(module_name)
                except ImportError as exc:
                    raise Exception('Artella Enterprise module is not available!: {}'.format(exc))
            reroute_fn = getattr(ENTERPRISE_MODULE, fn.__name__)

            reroute_fn_path = '{}.{}'.format(module_name, fn.__name__)
            if reroute_fn_path not in REROUTE_CACHE['enterprise']:
                REROUTE_CACHE['enterprise'][reroute_fn_path] = reroute_fn

            return REROUTE_CACHE['enterprise'][reroute_fn_path](*args, **kwargs)

        else:
            global INDIE_MODULE

            if 'indie' not in REROUTE_CACHE:
                REROUTE_CACHE['indie'] = dict()

            module_name = '{}.artellaindie'.format(base_module)
            if not INDIE_MODULE:
                try:
                    INDIE_MODULE = import_module(module_name)
                except ImportError as exc:
                    raise Exception('Artella Indie module is not available!: {}!'.format(exc))
            reroute_fn = getattr(INDIE_MODULE, fn.__name__)

            reroute_fn_path = '{}.{}'.format(module_name, fn.__name__)
            if reroute_fn_path not in REROUTE_CACHE['indie']:
                REROUTE_CACHE['indie'][reroute_fn_path] = reroute_fn

            return REROUTE_CACHE['indie'][reroute_fn_path](*args, **kwargs)

    return wrapper


# ===============================================================================================================

@reroute
@decorators.abstractmethod
def update_local_artella_root():
    """
    Updates the environment variable that stores the Artella Local Path
    NOTE: This is done by Artella plugin when is loaded, so we should not do it manually again
    """

    raise RuntimeError('update_local_artella_root function not implemented in Artella Abstract API!')


@reroute
@decorators.abstractmethod
def check_artella_plugin_loaded():
    """
    Returns True if the Artella plugin is loaded in Maya or False otherwise
    :return: bool
    """

    raise RuntimeError('check_artella_plugin_loaded function not implemented in Artella Abstract API!')


@reroute
@decorators.abstractmethod
def get_artella_data_folder():
    """
    Returns last version Artella folder installation
    :return: str
    """

    raise RuntimeError('get_artella_data_folder function not implemented in Artella Abstract API!')


@reroute
@decorators.abstractmethod
def update_artella_paths():
    """
    Updates system path to add artella paths if they are not already added
    :return:
    """

    raise RuntimeError('update_artella_paths function not implemented in Artella Abstract API!')


@reroute
@decorators.abstractmethod
def get_artella_python_folder():
    """
    Returns folder where Artella stores Python scripts
    :return: str
    """

    raise RuntimeError('get_artella_python_folder function not implemented in Artella Abstract API!')


@reroute
@decorators.abstractmethod
def get_artella_plugins_folder():
    """
    Returns folder where Artella stores its plugins
    :return: str
    """

    raise RuntimeError('get_artella_plugins_folder function not implemented in Artella Abstract API!')


@reroute
@decorators.abstractmethod
def get_artella_dcc_plugin(dcc='maya'):
    """
    Gets Artella DCC plugin depending of the given dcc string
    :param dcc: str, "maya" or "nuke"
    :return: str
    """

    raise RuntimeError('get_artella_dcc_plugin function not implemented in Artella Abstract API!')


@reroute
@decorators.abstractmethod
def get_artella_app():
    """
    Returns path where Artella path is installed
    :return: str
    """

    raise RuntimeError('get_artella_app function not implemented in Artella Abstract API!')


@reroute
@decorators.abstractmethod
def get_artella_program_folder():
    """
    Returns folder where Artella shortcuts are located
    :return: str
    """

    raise RuntimeError('get_artella_program_folder function not implemented in Artella Abstract API!')


@reroute
@decorators.abstractmethod
def get_artella_launch_shortcut():
    """
    Returns path where Launch Artella shortcut is located
    :return: str
    """

    raise RuntimeError('get_artella_launch_shortcut function not implemented in Artella Abstract API!')


@reroute
@decorators.abstractmethod
def launch_artella_app():
    """
    Executes Artella App
    """

    raise RuntimeError('launch_artella_app function not implemented in Artella Abstract API!')


@reroute
@decorators.abstractmethod
def close_all_artella_app_processes():
    """
    Closes all Artella app (lifecycler.exe) processes
    :return:
    """

    raise RuntimeError('close_all_artella_app_processes function not implemented in Artella Abstract API!')


@reroute
@decorators.abstractmethod
def connect_artella_app_to_spigot(cli=None, app_identifier=None):
    """
    Creates a new Spigot Client instance and makes it to listen
    to our current installed (and launched) Artella app
    """

    raise RuntimeError('connect_artella_app_to_spigot function not implemented in Artella Abstract API!')


@reroute
@decorators.abstractmethod
def spigot_listen(cli, app_id, handler):
    """
    Function that creates Spigot Thread.
    We use it in non DCC Python apps to properly close thread when the app is closed
    :param cli: SpigotClient
    :param appId:str
    :param handler: fn
    """

    raise RuntimeError('spigot_listen function not implemented in Artella Abstract API!')


@reroute
@decorators.abstractmethod
def load_artella_maya_plugin():
    """
    Loads the Artella plugin in the current Maya session
    :return: bool
    """

    raise RuntimeError('load_artella_maya_plugin function not implemented in Artella Abstract API!')


@reroute
@decorators.abstractmethod
def get_artella_client(app_identifier=None, force_create=True):
    """
    Creates, connects and returns an instance of the Spigot client
    :return: SpigotClient
    """

    raise RuntimeError('get_artella_client function not implemented in Artella Abstract API!')


@reroute
def get_artella_app_identifier():
    """
    Returns the installed Artella App identifier
    :return: variant, str || None
    """

    raise RuntimeError('get_artella_app_identifier function not implemented in Artella Abstract API!')


@reroute
@decorators.abstractmethod
def fix_path_by_project(project, path, fullpath=False):
    """
    Fix given path and updates to make it relative to the Artella project
    :param project: ArtellaProject
    :param path: str, path to be fixed
    :return: str
    """

    raise RuntimeError('fix_path_by_project function not implemented in Artella Abstract API!')


@reroute
@decorators.abstractmethod
def get_metadata():
    """
    Returns Artella App MetaData
    :return: ArtellaMetaData or None
    """

    raise RuntimeError('get_metadata function not implemented in Artella Abstract API!')


@reroute
@decorators.abstractmethod
def get_cms_uri(path):
    """
    Returns the CMS uri of the given path, if exists
    :param path: str
    :return: dict
    """

    raise RuntimeError('get_cms_uri function not implemented in Artella Abstract API!')


@reroute
@decorators.abstractmethod
def get_cms_uri_current_file():
    """
    Returns the CMS uri of the current file
    :return: str
    """

    raise RuntimeError('get_cms_uri_current_file function not implemented in Artella Abstract API!')


@reroute
@decorators.abstractmethod
def get_status(file_path, **kwargs):
    """
    Returns the status of  the given file path
    :param file_path: str
    :return: str
    """

    raise RuntimeError('get_status function not implemented in Artella Abstract API!')


@reroute
@decorators.abstractmethod
def get_status_current_file():
    """
    Returns the status of the current file
    :return:
    """

    raise RuntimeError('get_status function not implemented in Artella Abstract API!')


@reroute
@decorators.abstractmethod
def explore_file(path):
    """
    Opens the current file in the file explorer
    :param path: str
    """

    raise RuntimeError('get_status function not implemented in Artella Abstract API!')


@reroute
@decorators.abstractmethod
def pause_synchronization():
    """
    Pauses synchronization of files from Artella server
    """

    raise RuntimeError('pause_synchronization function not implemented in Artella Abstract API!')


@reroute
@decorators.abstractmethod
def resume_synchronization():
    """
    Resumes synchronization of files from Artella server
    """

    raise RuntimeError('resume_synchronization function not implemented in Artella Abstract API!')


@reroute
@decorators.abstractmethod
def get_synchronization_progress():
    """
    Returns the progress of the current Artella server synchronization operation
    Returns a tuple containing the following info:
        - amount of done download operations
        - amount of total download operations in progress
        - amount of total download operations that are going to be done
        - amount of total bytes downloaded
        - amount of total bytes to download
    :return: int, int, int, int, int
    """

    raise RuntimeError('get_synchronization_progress function not implemented in Artella Abstract API!')


@reroute
@decorators.abstractmethod
def synchronize_path(path):
    """
    Synchronize all the content of the given path, if exists
    :param path: str
    """

    raise RuntimeError('get_status function not implemented in Artella Abstract API!')


@reroute
@decorators.abstractmethod
def synchronize_file(file_path):
    """
    Synchronize the specific given file, if exists
    :param file_path: str
    :return:
    """

    raise RuntimeError('get_status function not implemented in Artella Abstract API!')


@reroute
@decorators.abstractmethod
def synchronize_path_with_folders(file_path, recursive=False, only_latest_published_versions=True):
    """
    Synchronizes given path and all its folders
    :param file_path: str
    :param recursive: bool
    :param only_latest_published_versions: bool
    :return:
    """

    raise RuntimeError('get_status function not implemented in Artella Abstract API!')


@reroute
@decorators.abstractmethod
def get_artella_project_url(project_id, files_url=True):
    """
    Returns Artella project URL
    :param project_id: str, Unique ID for the Artella project
    :param files_url: bool, Whether to return root project URL of project files URL
    :return: str
    """

    raise RuntimeError('get_artella_project_url function not implemented in Artella Abstract API!')
