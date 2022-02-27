#!/usr/bin/env bash

me=$(realpath $0)
log=$(dirname $me)/log
echo "$(date "+%Y-%m-%d %H:%M:%S") $PWD args: $@" >> $log
