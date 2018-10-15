#!/bin/bash
script=${1}
direc=${2}
addopts=${3}
name=${4}

for dc in ${direc}/*/datacard.txt; do
    cd $(dirname ${dc})
    ${script} datacard.txt "${addopts}" "${name}"
    cd - > /dev/null
done
