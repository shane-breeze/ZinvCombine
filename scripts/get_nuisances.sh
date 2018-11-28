#!/bin/bash
nuisances=$(cat ${1} | awk '{print $1}' | sed -e '1,/rate/d' | tail -n +2 | sed -e '/-----/,$d' | xargs -n1 | sort -u | xargs)
echo $nuisances
