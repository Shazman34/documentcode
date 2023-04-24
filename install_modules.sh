#!/bin/bash
for mod in netforce*; do
    echo "installing $mod..."
    cd $mod
    #./setup.py develop
    python3.10 setup.py develop
    cd ..
done
