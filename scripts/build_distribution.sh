#!/usr/bin/env bash

BASEDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

FRONT_END="$( $BASEDIR/build_frontend.sh )"


rm -rf dist && python -m build
