# -*- encoding: utf-8 -*-
import configparser
import os
import sys
import logging


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV = os.environ.get('ENV')
logger = logging.getLogger(__name__)


if ENV is None:
    logger.warning('Environment variable ENV is missing. Using development environment.')
    ENV = 'development'


def get_parser():
    base_config_path = os.path.join(BASE_DIR, 'config/base.ini')
    base_config_file = open(base_config_path)
    variable_config_path = os.path.join(BASE_DIR, 'config/{}.ini'.format(ENV))
    variable_config_file = open(variable_config_path)
    parser = configparser.ConfigParser()
    try:
        parser.read_file(base_config_file)
    except FileNotFoundError:
        logger.fatal('{} file was not found'.format(base_config_path))
        sys.exit(1)
    try:
        parser.read_file(variable_config_file)
    except FileNotFoundError:
        logger.fatal('{} file was not found'.format(variable_config_path))
        sys.exit(1)
    return parser
