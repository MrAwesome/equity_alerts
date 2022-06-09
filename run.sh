#!/usr/bin/env bash

while :; do
    python3 watch.py
    if [[ "$?" != "0" ]]; then
        echo "FAILURE"
        break
    fi
    sleep 3600
done
