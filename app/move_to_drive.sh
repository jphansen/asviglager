#!/bin/bash

# Will rename build package and copy it to google drive for jphansen.dk

DATE=$(date +"%Y%M%d%H%M%S")
SOURCE="build/app/outputs/flutter-apk"
DEST="/home/jph/Insync/jphansen.dk@gmail.com/Google Drive/APPS"

scp "$SOURCE/app-release.apk" "$DEST/asviglager-$DATE.apk"



