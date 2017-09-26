import os
import sys
import django
import configparser

sys.path.append("ezl")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ezl.settings")
django.setup()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
parser = configparser.ConfigParser()

try:
    with open(os.path.join(BASE_DIR, 'config', 'general.ini')) as config_file:
        parser.read_file(config_file)
        settings = dict(parser.items('etl'))

except FileNotFoundError:
    print('OOOOOOOOOOOOOOOOOOOOOOOOOOOHHHHH NOOOOOOOO!!!!!')
    print('general.ini file was not found on {config_path}'.format(config_path=os.path.join(BASE_DIR, 'config')))
    print('Rename it to general.ini and specify the correct configuration settings!')
    sys.exit(0)
