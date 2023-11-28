#!/bin/bash
# Path to your build script
/path/to/build.sh
# Starting the Django application with gunicorn
exec gunicorn my_project.wsgi:application --bind 0.0.0.0:8000
