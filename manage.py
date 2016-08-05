"""Default Django manage.py script."""

import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "apel_rest.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
