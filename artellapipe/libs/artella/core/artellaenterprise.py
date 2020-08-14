#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains Artella Enterprise API implementation
"""

import time
import logging
import traceback

import artella  # Do not remove

from artellapipe.libs.artella.core import artellaclasses

LOGGER = logging.getLogger('artellapipe-libs-artella')

global artella_client
artella_client = None


def init(dev=False):
    import artella.loader
    artella.loader.shutdown(dev=dev)
    artella.loader.init(dev=dev)


def update_local_artella_root():
    """
    Updates the environment variable that stores the Artella Local Path
    NOTE: This is done by Artella plugin when is loaded, so we should not do it manually again
    """

    metadata = get_metadata()
    if metadata:
        metadata.update_local_root()
        return True

    return False


def get_metadata():
    """
    Returns Artella App MetaData
    :return: ArtellaMetaData or None
    """

    client = get_artella_client()

    rsp = client.get_metadata()

    metadata = artellaclasses.ArtellaAppMetaData(
        local_root=rsp['workspace'],
        storage_id=rsp['machine-id'],
        openers_file=rsp['openers.log']
    )

    return metadata


def get_artella_client(app_identifier=None, force_create=True):
    """
    Creates, connects and returns an instance of the Spigot client
    :return: SpigotClient
    """

    global artella_client

    if artella_client is None and force_create:
        from artella.core import client
        artella_client = client.ArtellaDriveClient().get()

    return artella_client


def get_artella_python_folder():
    """
    Returns folder where Artella stores Python scripts
    :return: str
    """

    return None


def get_status(file_path, **kwargs):
    """
    Returns the status of  the given file path
    :param file_path: str
    :return: str
    """

    include_remote = kwargs.get('include_remote', False)

    client = get_artella_client()

    rsp = client.status(file_path, include_remote=include_remote)
    if not rsp:
        return dict()

    return rsp[0]


def pause_synchronization():
    """
    Pauses synchronization of files from Artella server
    """

    client = get_artella_client()

    return client.pause_downloads()


def resume_synchronization():
    """
    Resumes synchronization of files from Artella server
    """

    client = get_artella_client()

    return client.resume_downloads()


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

    client = get_artella_client()

    return client.get_progress()


def synchronize_path(path):
    """
    Synchronize all the content of the given path, if exists
    :param path: str
    """

    client = get_artella_client()

    try:
        valid = client.download(path)
    except Exception:
        LOGGER.error(traceback.format_exc())
        return False

    return valid


def synchronize_file(file_path):
    """
    Synchronize the specific given file, if exists
    :param file_path: str
    :return:
    """

    client = get_artella_client()

    try:
        valid = client.download(file_path)
    except Exception:
        LOGGER.error(traceback.format_exc())
        return False

    return valid


def synchronize_path_with_folders(file_path, recursive=False, only_latest_published_versions=True):
    """
    Synchronizes given path and all its folders
    :param file_path: str
    :param recursive: bool
    :param only_latest_published_versions: bool
    :return:
    """

    client = get_artella_client()

    valid = client.download(file_path, recursive=recursive)

    return valid
