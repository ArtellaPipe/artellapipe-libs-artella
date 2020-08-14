# #!/usr/bin/env python
# # -*- coding: utf-8 -*-

"""
Module that contains Artella Indie API implementation
"""

__all__ = [
    'getCmsUri', 'update_local_artella_root', 'check_artella_plugin_loaded', 'get_artella_data_folder',
    'update_artella_paths', 'get_artella_python_folder', 'get_artella_plugins_folder', 'get_artella_dcc_plugin',
    'get_artella_app', 'get_artella_program_folder', 'get_artella_launch_shortcut', 'launch_artella_app',
    'close_all_artella_app_processes', 'connect_artella_app_to_spigot', 'spigot_listen', 'load_artella_maya_plugin',
    'get_artella_client', 'get_artella_app_identifier', 'fix_path_by_project', 'get_metadata', 'get_cms_uri',
    'get_cms_uri_current_file', 'get_status', 'get_status_current_file', 'explore_file', 'pause_synchronization',
    'resume_synchronization', 'get_synchronization_progress', 'synchronize_path', 'synchronize_file',
    'synchronize_path_with_folders'
]

import os
import re
import sys
import json
import socket
import logging
import threading
import traceback

import tpDcc as tp
from tpDcc.libs.python import osplatform
from tpDcc.libs.qt.core import qtutils

import artellapipe
from artellapipe.libs import artella as artella_lib
from artellapipe.libs.artella.core import artellaclasses

LOGGER = logging.getLogger('artellapipe-libs-artella')

global artella_client
global spigot_thread

artella_client = None
spigot_thread = None


try:
    import Artella as art
    getCmsUri = art.getCmsUri
except ImportError:

    def getCmsUri(broken_path):
        path_parts = re.split(r'[/\\]', broken_path)
        while len(path_parts):
            path_part = path_parts.pop(0)
            if path_part == '_art':
                relative_path = '/'.join(path_parts)
                return relative_path
        return ''

# =================================================================================================================


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


def check_artella_plugin_loaded():
    """
    Returns True if the Artella plugin is loaded in Maya or False otherwise
    :return: bool
    """

    if tp.is_maya():
        return tp.Dcc.is_plugin_loaded('Artella')

    return False


def get_artella_data_folder():
    """
    Returns last version Artella folder installation
    :return: str
    """

    if osplatform.is_mac():
        artella_folder = os.path.join(os.path.expanduser('~/Library/Application Support/'), 'Artella')
    elif osplatform.is_windows():
        artella_folder = os.path.join(os.getenv('PROGRAMDATA'), 'Artella')
    else:
        return None

    next_version = artella_lib.config.get('app', 'next_version_filename')
    artella_app_version = None
    version_file = os.path.join(artella_folder, next_version)
    if os.path.isfile(version_file):
        with open(version_file) as f:
            artella_app_version = f.readline()

    if artella_app_version is not None:
        artella_folder = os.path.join(artella_folder, artella_app_version)
    else:
        artella_folder = [
            os.path.join(artella_folder, name) for name in os.listdir(artella_folder) if os.path.isdir(
                os.path.join(artella_folder, name)) and name != 'ui']
        if len(artella_folder) == 1:
            artella_folder = artella_folder[0]
        else:
            LOGGER.info('Artella folder not found!')

    LOGGER.debug('ARTELLA FOLDER: {}'.format(artella_folder))
    if not os.path.exists(artella_folder):
        qtutils.show_info(
            None, 'Artella Folder not found!',
            'Artella App Folder {} does not exists! Make sure that Artella is installed in your computer!')

    return artella_folder


def update_artella_paths():
    """
    Updates system path to add artella paths if they are not already added
    :return:
    """

    artella_folder = get_artella_data_folder()

    LOGGER.debug('Updating Artella paths from: {0}'.format(artella_folder))
    if artella_folder is not None and os.path.exists(artella_folder):
        for subdir, dirs, files in os.walk(artella_folder):
            if subdir not in sys.path:
                LOGGER.debug('Adding Artella path: {0}'.format(subdir))
                sys.path.append(subdir)


def get_artella_python_folder():
    """
    Returns folder where Artella stores Python scripts
    :return: str
    """

    return os.path.join(get_artella_data_folder(), 'python')


def get_artella_plugins_folder():
    """
    Returns folder where Artella stores its plugins
    :return: str
    """

    return os.path.join(get_artella_data_folder(), 'plugins')


def get_artella_dcc_plugin(dcc='maya'):
    """
    Gets Artella DCC plugin depending of the given dcc string
    :param dcc: str, "maya" or "nuke"
    :return: str
    """

    return os.path.join(get_artella_plugins_folder(), dcc)


def get_artella_app():
    """
    Returns path where Artella path is installed
    :return: str
    """

    artella_folder = os.path.dirname(get_artella_data_folder())
    artella_app_name = artella_lib.config.get('app', 'name')

    return os.path.join(artella_folder, artella_app_name)


def get_artella_program_folder():
    """
    Returns folder where Artella shortcuts are located
    :return: str
    """

    # TODO: This only works on Windows, find a cross-platform way of doing this

    return os.path.join(os.environ['PROGRAMDATA'], 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Artella')


def get_artella_launch_shortcut():
    """
    Returns path where Launch Artella shortcut is located
    :return: str
    """

    # TODO: This only works on Windows, find a cross-platform way of doing this

    return os.path.join(get_artella_program_folder(), 'Launch Artella.lnk')


def launch_artella_app():
    """
    Executes Artella App
    """

    # TODO: This should not work in MAC, find a cross-platform way of doing this

    if os.name == 'mac':
        LOGGER.info('Launch Artella App: does not supports MAC yet')
        qtutils.show_info(
            None,
            'Not supported in MAC',
            'Artella Pipeline do not support automatically Artella Launch for Mac. '
            'Please close Maya, launch Artella manually, and start Maya again!')
        artella_app_file = get_artella_app() + '.bundle'
    else:
        #  Executing Artella executable directly does not work
        # artella_app_file = get_artella_app() + '.exe'
        artella_app_file = get_artella_launch_shortcut()

    artella_app_file = artella_app_file
    LOGGER.info('Artella App File: {0}'.format(artella_app_file))

    if os.path.isfile(artella_app_file):
        LOGGER.info('Launching Artella App ...')
        LOGGER.debug('Artella App File: {0}'.format(artella_app_file))
        os.startfile(artella_app_file.replace('\\', '//'))


def close_all_artella_app_processes():
    """
    Closes all Artella app (lifecycler.exe) processes
    :return:
    """

    artella_app_name = artella_lib.config.get('app', 'name')

    psutil_available = False
    try:
        import psutil
        psutil_available = True
    except ImportError:
        pass

    if psutil_available:
        try:
            for proc in psutil.process_iter():
                if proc.name() == '{}.exe'.format(artella_app_name):
                    LOGGER.debug('Killing Artella App process: {}'.format(proc.name()))
                    proc.kill()
            return True
        except RuntimeError:
            LOGGER.error('Impossible to close Artella app instances because psutil library is not available!')
            return False

    return False


def connect_artella_app_to_spigot(cli=None, app_identifier=None):
    """
    Creates a new Spigot Client instance and makes it to listen
    to our current installed (and launched) Artella app
    """

    # TODO: Check if Artella App is launched and, is not, launch it

    def get_handle_msg(json_msg):
        if tp.is_houdini():
            try:
                msg = json.loads(json_msg)
            except Exception:
                LOGGER.warning('Unknown command!')
        else:
            return artella_lib.artella.handleMessage(json_msg)

    if cli is None:
        cli = get_artella_client()

    artella_app_identifier = get_artella_app_identifier()
    if not artella_app_identifier and app_identifier:
        artella_app_identifier = app_identifier

    if tp.is_maya():
        pass_msg_fn = artella_lib.artella.passMsgToMainThread
    elif tp.is_houdini():
        def pass_msg_to_main_thread(json_msg):
            from tpDcc.dccs.houdini.core import helpers
            main_thread_fn = helpers.get_houdini_pass_main_thread_function()
            main_thread_fn(get_handle_msg, json_msg)
        pass_msg_fn = pass_msg_to_main_thread
    else:
        def pass_msg(json_msg):
            get_handle_msg(json_msg)
        pass_msg_fn = pass_msg

    if tp.Dccs.Unknown:
        spigot_listen(cli, artella_app_identifier, pass_msg_fn)
    else:
        cli.listen(artella_app_identifier, pass_msg_fn)

    return cli


def spigot_listen(cli, app_id, handler):
    """
    Function that creates Spigot Thread.
    We use it in non DCC Python apps to properly close thread when the app is closed
    :param cli: SpigotClient
    :param appId:str
    :param handler: fn
    """

    global spigot_thread

    spigot_thread = threading.Thread(
        target=cli._pullMessages,
        args=(app_id, handler)
    )

    # Demonize thread to make sure that thread is automatically closed when Python interpreter is closed
    spigot_thread.daemon = True
    spigot_thread.start()


def load_artella_maya_plugin():
    """
    Loads the Artella plugin in the current Maya session
    :return: bool
    """

    if tp.is_maya():
        artella_plugin_name = artella_lib.config.get('app', 'plugin')
        LOGGER.debug('Loading Artella Maya Plugin: {} ...'.format(artella_plugin_name))
        artella_maya_plugin_folder = get_artella_dcc_plugin(dcc='maya')
        artella_maya_plugin_file = os.path.join(artella_maya_plugin_folder, artella_plugin_name)
        if os.path.isfile(artella_maya_plugin_file):
            if not tp.Dcc.is_plugin_loaded(artella_plugin_name):
                tp.Dcc.load_plugin(artella_maya_plugin_file)
                return True

    return False


def get_artella_client(app_identifier=None, force_create=True):
    """
    Creates, connects and returns an instance of the Spigot client
    :return: SpigotClient
    """

    global artella_client

    if artella_client is None and force_create:
        if tp.is_maya():
            from tpDcc.dccs.maya.core import gui
            gui.force_stack_trace_on()
        from am.artella.spigot.spigot import SpigotClient
        artella_client = SpigotClient()
        connect_artella_app_to_spigot(artella_client, app_identifier=app_identifier)

    return artella_client


def get_artella_app_identifier():
    """
    Returns the installed Artella App identifier
    :return: variant, str || None
    """

    app_identifier = os.environ.get('ARTELLA_APP_IDENTIFIER', None)
    if app_identifier is None:
        app_identifier = tp.Dcc.get_version_name()
        if tp.is_maya():
            app_identifier = 'maya.{}'.format(app_identifier.split()[0])

    return app_identifier


def fix_path_by_project(project, path, fullpath=False):
    """
    Fix given path and updates to make it relative to the Artella project
    :param project: ArtellaProject
    :param path: str, path to be fixed
    :return: str
    """

    artella_root_prefix = artella_lib.config.get('app', 'root_prefix')
    project_path = project.get_path()
    new_path = path.replace(project_path, '${}\\'.format(artella_root_prefix))
    if fullpath:
        new_path = path.replace(project_path, '${}'.format(artella_root_prefix) + '/' + project.full_id)
    return new_path


def get_metadata():
    """
    Returns Artella App MetaData
    :return: ArtellaMetaData or None
    """

    client = get_artella_client()

    try:
        rsp = client.execute(command_action='do', command_name='getMetaData', payload='{}')
    except socket.error as exc:
        # LOGGER.debug(exc)
        return None

    rsp = json.loads(rsp)

    metadata = artellaclasses.ArtellaAppMetaData(
        cms_web_root=rsp['cms_web_root'],
        local_root=rsp['local_root'],
        storage_id=rsp['storage_id'],
        token=rsp['token']
    )

    return metadata


def get_cms_uri(path):
    """
    Returns the CMS uri of the given path, if exists
    :param path: str
    :return: dict
    """

    if not path:
        return path

    path = os.path.normpath(path)
    cms_uri = getCmsUri(path)
    if not cms_uri:
        LOGGER.debug('Unable to get CMS uri from path: {0}'.format(path))
        return False

    req = json.dumps({'cms_uri': cms_uri})
    return req


def get_cms_uri_current_file():
    """
    Returns the CMS uri of the current file
    :return: str
    """

    current_file = tp.Dcc.scene_name()
    LOGGER.debug('Getting CMS Uri of file {0}'.format(current_file))

    cms_uri = getCmsUri(current_file)
    if not cms_uri:
        LOGGER.debug('Unable to get CMS uri from path: {0}'.format(current_file))
        return False

    LOGGER.debug('Retrieved CMS uri: {0}'.format(cms_uri))
    req = json.dumps({'cms_uri': cms_uri})

    return req


def get_status(file_path, **kwargs):
    """
    Returns the status of  the given file path
    :param file_path: str
    :return: str
    """

    as_json = kwargs.get('as_json', False)
    max_tries = kwargs.get('max_tries', 3)

    if max_tries > 50:
        max_tries = 50

    uri = get_cms_uri(file_path)
    if not uri:
        LOGGER.debug('Unable to get cmds uri from path: {}'.format(file_path))
        return False

    spigot = get_artella_client()

    current_try = 0
    rsp = None

    while current_try < max_tries:
        try:
            rsp = spigot.execute(command_action='do', command_name='status', payload=uri)
        except Exception as exc:
            LOGGER.debug(exc)
        if rsp and isinstance(rsp, (str, unicode)):
            try:
                rsp = json.loads(rsp)
                break
            except Exception:
                pass
        current_try += 1

    if current_try >= max_tries:
        msg = 'Artella is not available at this moment ... Restart Maya and try again please!'
        LOGGER.debug(msg)
        if artellapipe.project:
            artellapipe.project.message(msg)
        return {}

    if as_json:
        return rsp

    # Artella is down!!!!!
    if not rsp:
        msg = 'Artella is not available at this moment ... Restart Maya and try again please!'
        LOGGER.debug(msg)
        if artellapipe.project:
            artellapipe.project.message(msg)
        return None

    if 'data' in rsp:
        if '_latest' in rsp['data']:
            status_metadata = artellaclasses.ArtellaAssetMetaData(metadata_path=file_path, status_dict=rsp)
            return status_metadata

        status_metadata = artellaclasses.ArtellaDirectoryMetaData(metadata_path=file_path, status_dict=rsp)
    else:
        status_metadata = artellaclasses.ArtellaHeaderMetaData(header_dict=rsp['meta'])

    return status_metadata


def get_status_current_file():
    """
    Returns the status of the current file
    :return:
    """

    current_file = tp.Dcc.scene_name()
    LOGGER.debug('Getting Artella Status of file {0}'.format(current_file))

    status = get_status(current_file)
    LOGGER.debug('{0} STATUS -> {1}'.format(current_file, status))

    return status


def explore_file(path):
    """
    Opens the current file in the file explorer
    :param path: str
    """

    uri = get_cms_uri(path)
    spigot = get_artella_client()
    rsp = spigot.execute(command_action='do', command_name='explore', payload=uri)

    if isinstance(rsp, (unicode, str)):
        rsp = json.loads(rsp)

    return rsp


def pause_synchronization():
    """
    Pauses synchronization of files from Artella server
    """

    pass


def resume_synchronization():
    """
    Resumes synchronization of files from Artella server
    """

    pass


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

    return 0, 0, 0, 0, 0


def synchronize_path(path):
    """
    Synchronize all the content of the given path, if exists
    :param path: str
    """

    uri = get_cms_uri(path)
    spigot = get_artella_client()
    rsp = spigot.execute(command_action='do', command_name='updateCollection', payload=uri)

    if isinstance(rsp, (unicode, str)):
        rsp = json.loads(rsp)

    return rsp


def synchronize_file(file_path):
    """
    Synchronize the specific given file, if exists
    :param file_path: str
    :return:
    """

    try:
        uri = get_cms_uri(file_path)
        spigot = get_artella_client()
        rsp = spigot.execute(command_action='do', command_name='update', payload=uri)

        if isinstance(rsp, (unicode, str)):
            rsp = json.loads(rsp)

        return rsp
    except Exception:
        LOGGER.error(traceback.format_exc())
        return None


def synchronize_path_with_folders(file_path, recursive=False, only_latest_published_versions=True):
    """
    Synchronizes given path and all its folders
    :param file_path: str
    :param recursive: bool
    :param only_latest_published_versions: bool
    :return:
    """

    try:
        status = get_status(file_path)
        if isinstance(status, artellaclasses.ArtellaDirectoryMetaData):
            references = status.references
            for ref_name, ref_data in references.items():
                ref_path = ref_data.path
                if ref_data.is_directory:
                    synchronize_path(ref_path)
                    if recursive:
                        synchronize_path_with_folders(ref_path, recursive=True)
                else:
                    synchronize_file(ref_path)
            return True
        else:
            if os.path.isdir(file_path):
                child_dirs = list()
                # status = get_status(file_path)
                if isinstance(status, artellaclasses.ArtellaDirectoryMetaData):
                    for ref_name, ref_data in status.references.items():
                        dir_path = ref_data.path
                        if os.path.isdir(dir_path) or os.path.splitext(dir_path)[-1]:
                            continue
                        child_dirs.append(dir_path)
                elif isinstance(status, artellaclasses.ArtellaAssetMetaData):
                    working_folder = artellapipe.project.get_working_folder()
                    working_path = os.path.join(status.path, working_folder)
                    artella_data = get_status(working_path)
                    if isinstance(artella_data, artellaclasses.ArtellaDirectoryMetaData):
                        child_dirs.append(working_path)

                    if only_latest_published_versions:
                        published_versions = status.get_latest_published_versions(force_update=True)
                    else:
                        published_versions = status.get_published_versions(force_update=True)
                    if published_versions:
                        for version_name, version_data_list in published_versions.items():
                            for version_data in version_data_list:
                                version_path = version_data[2]
                                # No need to check path status because published versions function already does that
                                child_dirs.append(version_path)

                if child_dirs:
                    for child_dir in child_dirs:
                        synchronize_path_with_folders(child_dir, recursive=recursive)
                return True
    except Exception:
        LOGGER.error(traceback.format_exc())
        return None

    return False
