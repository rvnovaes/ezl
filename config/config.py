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
    filepath = os.path.join(BASE_DIR, 'config/{}.general.ini'.format(ENV))
    parser = configparser.ConfigParser()
    try:
        with open(filepath) as config_file:
            parser.read_file(config_file)
    except FileNotFoundError:
        logger.fatal('{} file was not found'.format(filepath))
        sys.exit(1)
    return parser
