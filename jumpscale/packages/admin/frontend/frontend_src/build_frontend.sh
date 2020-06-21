#!/bin/bash

rm -rf ../output/static/*
mkdir -p ../output/codebase
mkdir -p ../output/static/

# build will create the files directly inside ../output/codebase
if [ "$1" != "" ]; then
    npm run build-$1
else
    npm run build
fi

# copy index and static files
cp index.html ../output
cp -a static/* ../output/static
