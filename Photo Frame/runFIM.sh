#!/bin/bash
while :
do
find /home/pi -name *.jpg | shuf | fim -q -a -c "clear;while(_fileindex<_filelistlen){display;sleep 10;next;}sleep 10; clear; quit;" -
done
