#!/bin/bash
combine -M MultiDimFit --algo grid --points 20 --rMin 0.9 --rMax 1.1 ${1} -m 91 -n ZinvLLScan --expectSignal 1 -t -1
plot1DScan.py higgsCombineZinvLLScan.MultiDimFit.mH91.root --main-label Expected
