#!/usr/bin/env bash

make

for filename in MooshakTests/*; do
    [ -e "$filename" ] || continue
    echo "#### $filename ####"
    ./exercise < $filename | diff MooshakTestsOut/$(basename $filename) -
done
