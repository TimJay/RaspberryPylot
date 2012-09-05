'''
Short

Long ...

:author: TimJay@github
:date: 2012-09-05
:license: Creative Commons BY-NC-SA 3.0 [1]_

[1] http://creativecommons.org/licenses/by-nc-sa/3.0/deed.en_US
'''
import configparser

ground_config = configparser.ConfigParser()
ground_config_file = 'ground_config.ini'
ground_config.read(ground_config_file)

remote_config = configparser.ConfigParser()
remote_config_file = 'remote_config.ini'
remote_config.read(remote_config_file)


def save_ground_config():
    with open(ground_config_file, 'w') as configfile:
        ground_config.write(configfile)


def save_remote_config():
    with open(remote_config_file, 'w') as configfile:
        remote_config.write(configfile)
