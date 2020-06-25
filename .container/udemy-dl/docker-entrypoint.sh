#!/usr/bin/env bash
set -e
shopt -s extglob globstar

# Activate venv
source $VENV_HOME/bin/activate
cd $SRC_HOME
python udemy-dl.py --cookies ./cookies.txt --output $COURSE_HOME $UDEMYDL_ARGS $UDEMY_COURSE_URL

exec "$@"