#!/bin/bash
safety="--robustFit 1 --rMin 0.5 --rMax 1.5"
combineTool.py -M Impacts -m 91 -d ${1} --prefix-file ic --sub-opts "-q hep.q -e /dev/null -l h_rt=1:0:0" -n "${3}" ${safety} ${2}
