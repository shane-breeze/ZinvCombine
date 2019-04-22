#!/bin/bash
safety="--rMin 0.5 --rMax 1.5"
combineTool.py -M GoodnessOfFit -m 91 -d ${1} --prefix-file ic --sub-opts "-q hep.q -e /dev/null -o /dev/null -l h_rt=1:0:0" -n "${3}Obs" ${safety} ${2}
combineTool.py -M GoodnessOfFit -m 91 -d ${1} --prefix-file ic --sub-opts "-q hep.q -e /dev/null -o /dev/null -l h_rt=1:0:0" -n "${3}Toys" ${safety} -s 0:99:1 -t 10 ${2}
