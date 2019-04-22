#!/bin/bash
safety="--robustFit 1"
combineTool.py -M MultiDimFit -m 91 -d ${1} --task-name "LL2DSingles" --sub-opts "-q hep.q -e /dev/null -cwd -V -l h_rt=1:0:0" -n "LL2DScan${3}"   --algo singles ${safety} ${2}
combineTool.py -M MultiDimFit -m 91 -d ${1} --task-name "LL2DScan"    --sub-opts "-q hep.q -e /dev/null -cwd -V -l h_rt=1:0:0" -n "LL2DScan${3}"   --algo grid      --points 40000         ${safety} --split-points 100 --skipInitialFit --alignEdges 1 ${2}
combineTool.py -M MultiDimFit -m 91 -d ${1} --task-name "LL2DCont68"  --sub-opts "-q hep.q -e /dev/null -cwd -V -l h_rt=1:0:0" -n "LL2DCont68${3}" --algo contour2d --points 100 --cl=0.68 ${safety} --split-points 2   --skipInitialFit ${2}
combineTool.py -M MultiDimFit -m 91 -d ${1} --task-name "LL2DCont95"  --sub-opts "-q hep.q -e /dev/null -cwd -V -l h_rt=1:0:0" -n "LL2DCont95${3}" --algo contour2d --points 100 --cl=0.95 ${safety} --split-points 2   --skipInitialFit ${2}
