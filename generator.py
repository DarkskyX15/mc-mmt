'''
Date: 2024-05-11 20:45:58
Author: DarkskyX15
LastEditTime: 2024-05-21 16:55:57
'''

from os import walk as _walk
from os.path import join as _join
import os, re

def getMultiPaths(folder_path: str) -> tuple[list[str], list[str]]:
    r"""
    返回一对路径列表:`(file_paths, folder_paths)`
    - `file_paths`:`folder_path`下所有文件的路径列表
    - `folder_paths`:`folder_path`下所有文件夹的路径列表 (包括`folder_path`本身)
    """
    file_path_list = list()
    folder_list = list()
    for filepath, folder_names, filenames in _walk(folder_path):
        for filename in filenames:
            file_path_list.append(_join(filepath, filename))
        folder_list.append(filepath)
    return (file_path_list, folder_list)

def readConfigFile(path: str) -> dict[str, str]:
    config_dict = {}
    with open(path, 'r') as f:
        config_lines = f.read().splitlines()
    for line in config_lines:
        setting_pair = line.split(' ')
        config_dict[setting_pair[0]] = setting_pair[1]
    return config_dict

DATA_PATH = '.\\data'
GENERATE_PATH = '.\\generated'
SRC_PATH = '.\\resources'

# Settings
PUT_TO_DATA = False

# Global var
games = []
map_config = {}

class Game:
    def __init__(self, game_name: str) -> None:
        self.game_name: str = game_name
        self.launch_path: str = None
        self.uninstall_path: str = None
        self.install_path: str = None
        self.stop_path: str = None
        self.value_dict: dict[str, str] = {}

def processModule(root: str, namespace: str, save_path: str) -> None:
    file_names, folders = getMultiPaths(root)
    for folder in folders:
        relevant = folder.removeprefix(root)
        if not relevant: relevant = '\\'
        folder_path = save_path + '\\' + namespace + relevant
        os.mkdir(folder_path)
        print('Make dir:', folder_path)
    # Check config
    try:
        config = readConfigFile(_join(root, 'config.txt'))
    except FileNotFoundError:
        print('Can not find config.txt in module:', namespace)
        return
    # IGNORED setting
    try:    
        if config['IGNORED'] == 'true':
            print('Skip processing for', namespace)
            return
    except KeyError:
        print('Can not find IGNORED setting, default false')
    # GAME_NAME setting
    try:
        game_name = config['GAME_NAME']
        game_name = ' '.join(game_name.split('_'))
        print('Found game name:', game_name)
    except KeyError:
        print('Can not find game name for module:', namespace)
        return
    # Create game instance
    game = Game(' '.join(game_name.split('_')))
    # Set values
    for item in config.items():
        if item[0] != 'IGNORED' and item[0] != 'GAME_NAME':
            arg = item[1].split('|')
            if len(arg) == 2 and arg[0] == 'BIND':
                game.value_dict[item[0]] = map_config.get(item[0], arg[1])
            else:
                game.value_dict[item[0]] = arg[0]
    function_validation = 0
    # Check launch.mcfunction
    launch_path = root + '\\functions\\launch.mcfunction'
    if os.path.exists(launch_path):
        print('Found launch function:', launch_path)
        game.launch_path = launch_path
        function_validation += 1
    # Check stop.mcfunction
    stop_path = root + '\\functions\\stop.mcfunction'
    if os.path.exists(stop_path):
        print('Found stop function:', stop_path)
        game.stop_path = stop_path
        function_validation += 1
    # Check install.mcfunction
    install_path = root + '\\functions\\install.mcfunction'
    if os.path.exists(install_path):
        print('Found install function:', install_path)
        game.install_path = install_path
        function_validation += 1
    # Check uninstall.mcfunction
    uninstall_path = root + '\\functions\\uninstall.mcfunction'
    if os.path.exists(uninstall_path):
        print('Found uninstall function:', uninstall_path)
        game.uninstall_path = uninstall_path
        function_validation += 1
    if function_validation < 4:
        print('Function requirement not met! Skip processing.')
        return
    # push game
    games.append(game)

if __name__ == '__main__':
    save_path = DATA_PATH if PUT_TO_DATA else GENERATE_PATH
    # Clean Cache
    print('Deleting caches...')
    file_names, folder_names = getMultiPaths(save_path)
    for file_name in file_names:
        os.remove(file_name)
        print('Removed:', file_name)
    for dir_name in folder_names[:0:-1]:
        os.rmdir(dir_name)
        print('Removed:', dir_name)
    
    # Get map config
    map_config = readConfigFile(SRC_PATH + '\\mmt_map\\config.txt')
    print('Loaded global values:', map_config)

    # Process each dir
    namespaces = [namespace for namespace in os.listdir(SRC_PATH)\
                  if namespace != 'mmt_map' and namespace != 'mmt_core']
    print('Found modules:', namespaces)
    for namespace in namespaces:
        print('---------------\nProcessing module:', namespace)
        processModule(_join(SRC_PATH, namespace), namespace, save_path)
    
