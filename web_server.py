#!/usr/bin/env python
import os
import sys
from atari_manager import startup, parse_args

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "atari_django.settings")

    from django.core.management import execute_from_command_line

    args = parse_args()
    startup(args)

    execute_from_command_line([sys.executable, "runserver", "0.0.0.0:80", "--noreload"])
