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


@reroute
@decorators.abstractmethod
def split_version(name, next_version=False):
    """
    Returns the version of a specific given asset (model_v001, return [v001, 001, 1])
    :param name: str
    :param next_version: bool
    :return: list(str, int, int)
    """

    raise RuntimeError('split_version function not implemented in Artella Abstract API!')


@reroute
@decorators.abstractmethod
def get_file_history(file_path, as_json=False):
    """
    Returns the history info of the given file, if exists
    :param file_path: str
    :param as_json: bool
    """

    raise RuntimeError('get_file_history function not implemented in Artella Abstract API!')


@reroute
@decorators.abstractmethod
def get_asset_image(asset_path, project_id):
    """
    Returns the asset image from Artella server
    :param asset_path: str, path of the asset relative to the Assets folder
    :param project_id: str, ID of the Artella project you are currently working
    :return:
    """

    raise RuntimeError('get_asset_image function not implemented in Artella Abstract API!')


@reroute
@decorators.abstractmethod
def launch_maya(file_path, maya_version=None):
    """
    :param file_path: str
    :param maya_version: int
    :return:
    """

    raise RuntimeError('launch_maya function not implemented in Artella Abstract API!')


@reroute
@decorators.abstractmethod
def open_file_in_maya(file_path, maya_version=None):
    """
    Open the given path in the given Maya version
    :param file_path: str
    :param maya_version: int
    """

    raise RuntimeError('open_file_in_maya function not implemented in Artella Abstract API!')


@reroute
@decorators.abstractmethod
def import_file_in_maya(file_path, maya_version=None):
    """
    Import the given asset path in the given Maya version current scene
    :param file_path: str
    :param maya_version: int
    """

    raise RuntimeError('import_file_in_maya function not implemented in Artella Abstract API!')


@reroute
@decorators.abstractmethod
def reference_file_in_maya(file_path, maya_version=None):
    """
    Import the given asset path in the given Maya version current scene
    :param file_path: str
    :param maya_version: int
    """

    raise RuntimeError('reference_file_in_maya function not implemented in Artella Abstract API!')


@reroute
@decorators.abstractmethod
def is_published(file_path):
    """
    Returns whether an absolute file path refers to a published asset
    :param file_path: str, absolute path to a file
    :return: bool
    """

    raise RuntimeError('is_published function not implemented in Artella Abstract API!')


@reroute
@decorators.abstractmethod
def is_updated(file_path):
    """
    Returns whether or not given file path is updated to the last version
    :param file_path: str
    :return: bool
    """

    raise RuntimeError('is_updated function not implemented in Artella Abstract API!')


@reroute
@decorators.abstractmethod
def is_locked(file_path):
    """
    Returns whether an absolute file path refers to a locked asset in edit mode, and if the file is locked
    by the current storage workspace
    :param file_path: str, absolute path to a file
    :return: (bool, bool), Whether file is locked or not, whether the file is locked by another user or not
    """

    raise RuntimeError('is_locked function not implemented in Artella Abstract API!')


@reroute
@decorators.abstractmethod
def lock_file(file_path=None, force=False):
    """
    Locks given file path
    :param file_path: str
    :param force: bool
    """

    raise RuntimeError('lock_file function not implemented in Artella Abstract API!')


@reroute
@decorators.abstractmethod
def upload_file(file_path, comment):
    """
    Uploads a new version of the given file to Artella server
    :param file_path: str
    :param comment: str
    """

    raise RuntimeError('upload_file function not implemented in Artella Abstract API!')


@reroute
@decorators.abstractmethod
def get_current_user_id():
    """
    Returns Artella ID of the current user
    :return: str
    """

    raise RuntimeError('get_current_user_id function not implemented in Artella Abstract API!')


@reroute
@decorators.abstractmethod
def can_unlock(file_path, **kwargs):
    """
    Returns whether given path can be unlocked or not by current user
    :param file_path: str
    :return: bool
    """

    raise RuntimeError('can_unlock function not implemented in Artella Abstract API!')


@reroute
@decorators.abstractmethod
def unlock_file(file_path, **kwargs):
    """
    Unlocks a given file path
    :param file_path:
    """

    raise RuntimeError('unlock_file function not implemented in Artella Abstract API!')


@reroute
@decorators.abstractmethod
def upload_new_asset_version(file_path=None, comment='Published new version with Artella Pipeline', skip_saving=False):
    """
    Adds a new file to the Artella server
    :param file_path:
    :param comment:
    :param skip_saving: When we publish textures we do not want to save the maya scene
    """

    raise RuntimeError('upload_new_asset_version function not implemented in Artella Abstract API!')


@reroute
@decorators.abstractmethod
def publish_asset(asset_path, comment, selected_versions, version_name):
    """
    Publish a new version of the given asset
    :param asset_path:
    :param comment:
    :param selected_versions:
    :param version_name:
    """

    raise RuntimeError('publish_asset function not implemented in Artella Abstract API!')


@reroute
@decorators.abstractmethod
def get_local_working_version(file_path):
    """
    Returns current version of the given file in Artella server
    :param file_path: str
    :return: int
    """

    raise RuntimeError('get_local_working_version function not implemented in Artella Abstract API!')


@reroute
@decorators.abstractmethod
def get_current_version(file_path):
    """
    Returns current published version of the given file path in Artella server
    :param file_path: str
    :return: int
    """

    raise RuntimeError('get_current_version function not implemented in Artella Abstract API!')


@reroute
@decorators.abstractmethod
def get_latest_version(file_path, check_validity=True):
    """
    Returns last version of the given file path in Artella server
    :param file_path: str
    :param check_validity: bool
    :return: int
    """

    raise RuntimeError('get_latest_version function not implemented in Artella Abstract API!')


@reroute
@decorators.abstractmethod
def within_artella_scene():
    """
    Returns True if the current Maya scene corresponds to a Artella Maya scene
    :return: bool
    """

    raise RuntimeError('within_artella_scene function not implemented in Artella Abstract API!')


@reroute
@decorators.abstractmethod
def get_user_avatar(user_id):
    """
    Downloads from Artella the avatar of the given user id
    Only works if the user is loaded before to Artella
    :param user_id: str
    :return:
    """

    raise RuntimeError('get_user_avatar function not implemented in Artella Abstract API!')


@reroute
@decorators.abstractmethod
def get_dependencies(file_path):
    """
    Returns a list with all the dependencies
    :param file_path: str
    :return: dict
    """

    raise RuntimeError('get_dependencies function not implemented in Artella Abstract API!')


@reroute
@decorators.abstractmethod
def create_asset(asset_name, asset_path):
    """
    Creates an asset with given name and in given path
    :param asset_name: str
    :param asset_path: str
    :return: dict
    """

    raise RuntimeError('create_asset function not implemented in Artella Abstract API!')


@reroute
@decorators.abstractmethod
def delete_file(file_path):
    """
    Removes given file from Artella server
    :param file_path: str
    :return: dict
    """

    raise RuntimeError('delete_file function not implemented in Artella Abstract API!')


@reroute
@decorators.abstractmethod
def rename_file(file_path, new_name):
    """
    Renames given file with new given name
    :param file_path: str
    :param new_name: str
    """

    raise RuntimeError('rename_file function not implemented in Artella Abstract API!')


@reroute
@decorators.abstractmethod
def new_folder(root_path, folder_name):
    """
    Creates a new folder in the given path
    :param root_path: str
    :param folder_name: str
    """

    raise RuntimeError('new_folder function not implemented in Artella Abstract API!')
