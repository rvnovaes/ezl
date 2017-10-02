#!/usr/bin/python
# -*- encoding: utf-8 -*-

import os
import sys
import configparser
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)


def get_parser():
    parser = configparser.ConfigParser()
    try:
        with open(os.path.join(BASE_DIR, 'config', 'general.ini')) as config_file:
            parser.read_file(config_file)
    except FileNotFoundError:
        print('OOOOOOOOOOOOOOOOOOOOOOOOOOOHHHHH NOOOOOOOO!!!!!')
        print('general.ini file was not found on {config_path}'.format(config_path=os.path.join(BASE_DIR, 'config')))
        print('Rename it to general.ini and specify the correct configuration settings!')
        sys.exit(0)
    return parser
