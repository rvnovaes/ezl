import os
import sys
import django

sys.path.append("ezl")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ezl.settings")
django.setup()
