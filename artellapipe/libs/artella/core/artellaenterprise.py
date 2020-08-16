#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains Artella Enterprise API implementation
"""

import os
import logging
import traceback
from collections import OrderedDict

import tpDcc as tp
from tpDcc.libs.qt.core import qtutils

import artellapipe
from artellapipe.libs.artella.core import artellaclasses

LOGGER = logging.getLogger('artellapipe-libs-artella')

global artella_client
artella_client = None


def init(dev=False):
    import artella.loader
    artella.loader.shutdown(dev=dev, cleanup_modules=True)
    artella.loader.init(dev=dev, create_menu=False, create_callbacks=False)


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


def get_artella_project_url(project_id, files_url=True):
    """
    Returns Artella project URL
    :param project_id: str, Unique ID for the Artella project
    :param files_url: bool, Whether to return root project URL of project files URL
    :return: str
    """

    client = get_artella_client()

    artella_web = artellapipe.libs.artella.config.get('server', dict()).get('url', 'https://www.artella.com')

    project_api = None
    projects = client.get_local_projects() or dict()
    for project_name, project_data in projects.items():
        project_remote = project_data.get('remote', None)
        if not project_remote:
            continue
        if project_remote == project_id:
            project_api = project_data.get('api', None)
            break

    if not project_api:
        remote_projects = client.get_remote_projects()
        if not remote_projects:
            return
        for remote_api, projects_data in remote_projects.items():
            if not projects_data:
                continue
            for project_remote, project_data in projects_data.items():
                if project_remote == project_id:
                    break
    if not project_api:
        LOGGER.warning('No Project API for project with ID: {}'.format(project_id))
        return artella_web

    clean_api = project_api.replace('-api.', '.')
    clean_id = project_id.replace('project__', '')

    if files_url:
        return '{}/project/{}/files/p'.format(clean_api, clean_id)

    return '{}/project/{}/feed/all'.format(clean_api, clean_id)


def get_file_history(file_path, as_json=False):
    """
    Returns the history info of the given file, if exists
    :param file_path: str
    :param as_json: bool
    """

    client = get_artella_client()

    status = client.status(file_path, include_remote=True)

    versions = OrderedDict()
    for file_status in status:
        for file_uri_path, file_status_data in file_status.items():
            if 'local_info' not in file_status_data or not file_status_data['local_info'] or \
                    'remote_info' not in file_status_data:
                continue
            else:
                current_version = file_status_data['remote_info'].get('version', 0)
                versions[current_version] = file_status_data

    return versions


def is_published(file_path):
    """
    Returns whether an absolute file path refers to a published asset
    :param file_path: str, absolute path to a file
    :return: bool
    """

    return False


def is_updated(file_path):
    """
    Returns whether or not given file path is updated to the last version
    :param file_path: str
    :return: bool
    """

    client = get_artella_client()

    file_is_latest_version = client.file_is_latest_version(file_path)

    return file_is_latest_version


def is_locked(file_path):
    """
    Returns whether an absolute file path refers to a locked asset in edit mode, and if the file is locked
    by the current storage workspace
    :param file_path: str, absolute path to a file
    :return: (bool, bool), Whether file is locked or not, whether the file is locked by another user or not
    """

    client = get_artella_client()

    file_is_locked, is_locked_by_me, _, _ = client.check_lock(file_path)

    return file_is_locked, is_locked_by_me


def lock_file(file_path=None, force=False):
    """
    Locks given file path
    :param file_path: str
    :param force: bool
    """

    if not file_path:
        file_path = tp.Dcc.scene_name()
    if not file_path:
        LOGGER.error('File {} cannot be locked because it does not exists!'.format(file_path))
        return False

    file_published = is_published(file_path)
    if file_published:
        msg = 'Current file ({}) is published and cannot be edited'.format(os.path.basename(file_path))
        LOGGER.info(msg)
        if hasattr(artellapipe, 'project') and artellapipe.project:
            artellapipe.project.message(msg)
        return False

    client = get_artella_client()

    can_write = os.access(file_path, os.W_OK)
    if not can_write:
        msg = 'Unable to check local write permissions for file: {}'.format(file_path)
        LOGGER.info(msg)
        if artellapipe.project:
            artellapipe.project.message(msg)

    valid_lock = False
    can_lock = client.can_lock_file(file_path)
    if can_lock or force:
        valid_lock = bool(client.lock_file(file_path))

    if not valid_lock:
        msg = 'Unable to lock file: {}'.format(file_path)
        LOGGER.info(msg)
        if artellapipe.project:
            artellapipe.project.message(msg)

    return valid_lock


def unlock_file(file_path, **kwargs):
    """
    Unlocks a given file path
    :param file_path:
    """

    force = kwargs.get('force', False)

    if not can_unlock(file_path, force=force):
        LOGGER.debug('Impossible to unlock file!')
        return False

    client = get_artella_client()

    rsp = client.unlock_file(file_path)
    valid_lock = all(res is True for res in list(rsp.values()))

    return valid_lock


def can_unlock(file_path, **kwargs):
    """
    Returns whether given path can be unlocked or not by current user
    :param file_path: str
    """

    force = kwargs.get('force', False)

    file_is_locked, is_locked_by_me = is_locked(file_path)
    if not file_is_locked:
        return False

    if force or (file_is_locked and is_locked_by_me):
        return True

    return False


def upload_new_asset_version(file_path=None, comment='Published new version with Artella Pipeline', skip_saving=False):
    """
    Adds a new file to the Artella server
    :param file_path:
    :param comment:
    :param skip_saving: When we publish textures we do not want to save the maya scene
    """

    if not file_path:
        file_path = tp.Dcc.scene_name()
    if not file_path:
        LOGGER.error('File {} cannot be locked because it does not exists!'.format(file_path))
        return False

    msg = 'Making new version for {}'.format(file_path)
    LOGGER.info(msg)
    if artellapipe.project:
        artellapipe.project.message(msg)

    client = get_artella_client()

    valid_upload = False
    if file_path is not None and file_path != '':
        file_is_locked, is_locked_by_me, _, _ = client.check_lock(file_path)
        if file_is_locked and not is_locked_by_me:
            error_msg = 'File is locked by other user. Impossible to create new version'
            LOGGER.error(error_msg)
            if artellapipe.project:
                artellapipe.project.message(error_msg)
            return False

        if not skip_saving:
            if tp.Dcc.scene_is_modified():
                tp.Dcc.save_current_scene(force=True)

        if tp.is_maya():
            from tpDcc.dccs.maya.core import helpers
            if helpers.file_has_student_line(filename=file_path):
                helpers.clean_student_line(filename=file_path)
                if helpers.file_has_student_line(filename=file_path):
                    LOGGER.error('After updating model path the Student License could not be fixed again!')
                    return False

        msg = 'Saving new file version on Artella Server: {}'.format(file_path)
        LOGGER.info(msg)
        if artellapipe.project:
            artellapipe.project.message(msg)
        if comment is None:
            result = tp.Dcc.confirm_dialog(
                title='Artella Pipeline - Save New Version on Artella Server', message=msg, button=['Save', 'Cancel'],
                cancel_button='Cancel', dismiss_string='Cancel')
            if result == 'Save':
                comment = qtutils.get_comment(title='Comment')
            else:
                return False

        valid_upload = client.upload(file_path, comment=comment)
    else:
        msg = 'The file has not been created yet'
        LOGGER.debug(msg)
        tp.Dcc.warning(msg)
        tp.Dcc.confirm_dialog(title='Artella Pipeline - Failed to Make New Version', message=msg, button=['Ok'])

    if not valid_upload:
        msg = 'Failed to make new version of {}'.format(os.path.basename(file_path))
        tp.Dcc.confirm_dialog(title='Artella Pipeline - Failed to Make New Version', message=msg, button=['Ok'])
        return False

    return valid_upload


def get_local_working_version(file_path):
    """
    Returns current version of the given file in Artella server
    :param file_path: str
    :return: int
    """

    if not file_path or not os.path.exists(file_path):
        return -1

    client = get_artella_client()

    current_version = client.file_current_version(file_path=file_path)

    return current_version


def get_current_version(file_path):
    """
    Returns current published version of the given file path in Artella server
    :param file_path: str
    :return: int
    """

    return get_local_working_version(file_path)
