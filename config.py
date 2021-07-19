# For reading config files
from configparser import ConfigParser
import os
import sys


class Config(object):

    def __init__(self, config_file):
        ''' Initialise class '''
        # Get database location from config file
        self.Main = Main(config_file)
        self.Sym = Sym(config_file)


class Main(object):

    def __init__(self, config_file):
        ''' Initialise class '''
        # Get database location from config file
        self.database_path_fe = config_file['Directories']['Database Path (Front End)']


class Sym(object):

    def __init__(self, config_file):
        ''' Initialise class '''
        # Get database location from config file
        self.test = config_file['Sym']['test']


# Read config stuff
basedir = os.path.dirname(sys.argv[0])
config_path = os.path.join(basedir, 'config_file.cfg')
config_file = ConfigParser()
config_file.read(config_path)
Config = Config(config_file)
