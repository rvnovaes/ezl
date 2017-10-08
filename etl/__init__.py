import os
import sys
import django
import configparser
from config.config import get_parser


sys.path.append("ezl")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ezl.settings")
django.setup()

parser = get_parser()
