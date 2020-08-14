#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains Artella Abstract API implementation
"""

import os

from tpDcc.libs.python import decorators


def update_local_artella_root():
    """
    Updates the environment variable that stores the Artella Local Path
    NOTE: This is done by Artella plugin when is loaded, so we should not do it manually again
    """

    raise RuntimeError('update_local_artella_root function not implemented in Artella Abstract API!')


def check_artella_plugin_loaded():
    """
    Returns True if the Artella plugin is loaded in Maya or False otherwise
    :return: bool
    """

    raise RuntimeError('check_artella_plugin_loaded function not implemented in Artella Abstract API!')


@decorators.abstractmethod
def get_artella_data_folder():
    """
    Returns last version Artella folder installation
    :return: str
    """

    raise RuntimeError('get_artella_data_folder function not implemented in Artella Abstract API!')


@decorators.abstractmethod
def update_artella_paths():
    """
    Updates system path to add artella paths if they are not already added
    :return:
    """

    raise RuntimeError('update_artella_paths function not implemented in Artella Abstract API!')


@decorators.abstractmethod
def get_artella_python_folder():
    """
    Returns folder where Artella stores Python scripts
    :return: str
    """

    raise RuntimeError('get_artella_python_folder function not implemented in Artella Abstract API!')


@decorators.abstractmethod
def get_artella_plugins_folder():
    """
    Returns folder where Artella stores its plugins
    :return: str
    """

    raise RuntimeError('get_artella_plugins_folder function not implemented in Artella Abstract API!')


@decorators.abstractmethod
def get_artella_dcc_plugin(dcc='maya'):
    """
    Gets Artella DCC plugin depending of the given dcc string
    :param dcc: str, "maya" or "nuke"
    :return: str
    """

    raise RuntimeError('get_artella_dcc_plugin function not implemented in Artella Abstract API!')


@decorators.abstractmethod
def get_artella_app():
    """
    Returns path where Artella path is installed
    :return: str
    """

    raise RuntimeError('get_artella_app function not implemented in Artella Abstract API!')


@decorators.abstractmethod
def get_artella_program_folder():
    """
    Returns folder where Artella shortcuts are located
    :return: str
    """

    raise RuntimeError('get_artella_program_folder function not implemented in Artella Abstract API!')


@decorators.abstractmethod
def get_artella_launch_shortcut():
    """
    Returns path where Launch Artella shortcut is located
    :return: str
    """

    raise RuntimeError('get_artella_launch_shortcut function not implemented in Artella Abstract API!')


@decorators.abstractmethod
def launch_artella_app():
    """
    Executes Artella App
    """

    raise RuntimeError('launch_artella_app function not implemented in Artella Abstract API!')


@decorators.abstractmethod
def close_all_artella_app_processes():
    """
    Closes all Artella app (lifecycler.exe) processes
    :return:
    """

    raise RuntimeError('close_all_artella_app_processes function not implemented in Artella Abstract API!')


@decorators.abstractmethod
def connect_artella_app_to_spigot(cli=None, app_identifier=None):
    """
    Creates a new Spigot Client instance and makes it to listen
    to our current installed (and launched) Artella app
    """

    raise RuntimeError('connect_artella_app_to_spigot function not implemented in Artella Abstract API!')


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


@decorators.abstractmethod
def load_artella_maya_plugin():
    """
    Loads the Artella plugin in the current Maya session
    :return: bool
    """

    raise RuntimeError('load_artella_maya_plugin function not implemented in Artella Abstract API!')


@decorators.abstractmethod
def get_artella_client(app_identifier=None, force_create=True):
    """
    Creates, connects and returns an instance of the Spigot client
    :return: SpigotClient
    """

    raise RuntimeError('get_artella_client function not implemented in Artella Abstract API!')


def get_artella_app_identifier():
    """
    Returns the installed Artella App identifier
    :return: variant, str || None
    """

    raise RuntimeError('get_artella_app_identifier function not implemented in Artella Abstract API!')


@decorators.abstractmethod
def fix_path_by_project(project, path, fullpath=False):
    """
    Fix given path and updates to make it relative to the Artella project
    :param project: ArtellaProject
    :param path: str, path to be fixed
    :return: str
    """

    raise RuntimeError('fix_path_by_project function not implemented in Artella Abstract API!')


@decorators.abstractmethod
def get_metadata():
    """
    Returns Artella App MetaData
    :return: ArtellaMetaData or None
    """

    raise RuntimeError('get_metadata function not implemented in Artella Abstract API!')


@decorators.abstractmethod
def get_cms_uri(path):
    """
    Returns the CMS uri of the given path, if exists
    :param path: str
    :return: dict
    """

    raise RuntimeError('get_cms_uri function not implemented in Artella Abstract API!')


@decorators.abstractmethod
def get_cms_uri_current_file():
    """
    Returns the CMS uri of the current file
    :return: str
    """

    raise RuntimeError('get_cms_uri_current_file function not implemented in Artella Abstract API!')


@decorators.abstractmethod
def get_status(file_path, **kwargs):
    """
    Returns the status of  the given file path
    :param file_path: str
    :return: str
    """

    raise RuntimeError('get_status function not implemented in Artella Abstract API!')


@decorators.abstractmethod
def get_status_current_file():
    """
    Returns the status of the current file
    :return:
    """

    raise RuntimeError('get_status function not implemented in Artella Abstract API!')


@decorators.abstractmethod
def explore_file(path):
    """
    Opens the current file in the file explorer
    :param path: str
    """

    raise RuntimeError('get_status function not implemented in Artella Abstract API!')


@decorators.abstractmethod
def pause_synchronization():
    """
    Pauses synchronization of files from Artella server
    """

    raise RuntimeError('pause_synchronization function not implemented in Artella Abstract API!')


@decorators.abstractmethod
def resume_synchronization():
    """
    Resumes synchronization of files from Artella server
    """

    raise RuntimeError('resume_synchronization function not implemented in Artella Abstract API!')


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


@decorators.abstractmethod
def synchronize_path(path):
    """
    Synchronize all the content of the given path, if exists
    :param path: str
    """

    raise RuntimeError('get_status function not implemented in Artella Abstract API!')


@decorators.abstractmethod
def synchronize_file(file_path):
    """
    Synchronize the specific given file, if exists
    :param file_path: str
    :return:
    """

    raise RuntimeError('get_status function not implemented in Artella Abstract API!')


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
