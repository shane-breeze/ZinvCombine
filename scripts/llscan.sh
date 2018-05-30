#!/bin/bash
combine -M MultiDimFit --algo grid --points 100 --rMin 0.9 --rMax 1.3 ${1} -m 91 -n ZinvLLScan --expectSignal 1
plot1DScan.py higgsCombineZinvLLScan.MultiDimFit.mH91.root
