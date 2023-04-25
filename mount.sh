#!/usr/bin/bash

set -e -o pipefail

# export the following or add them to your ~/.bashrc
# export AIALBUM_USER="AIALBUM_USER"
# export AIALBUM_PASS="AIALBUM_PASS"
# export AIALBUM_SMBPATH="AIALBUM_SMBPATH"
# export AIALBUM_SMBNAME="AIALBUM_SMBNAME"

# Run the following
AIALBUM_SMBPATH_FULL="//`avahi-resolve -n \"$AIALBUM_SMBNAME\" -4 | cut -f2`/\"$AIALBUM_SMBPATH\""

echo "Run the following command to mount"
echo ">>"
echo ">>" sudo mount.cifs  "$AIALBUM_SMBPATH_FULL" ./data/  --verbose  -o user=$(whoami),uid=`id -u`,gid=`id -g`,ro,username=\"$AIALBUM_USER\",domain=WORKGROUP,password=\"$AIALBUM_PASS\" 
echo ">>"

echo "Run the following command to unmount"
echo ">>"
echo ">>" sudo umount ./data
echo ">>"