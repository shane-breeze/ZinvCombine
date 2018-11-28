#!/bin/bash
safety="--robustFit 1"
combine -n LL1DSingles${3} -M MultiDimFit --algo singles ${1} ${safety} --expectSignal 1 ${2}
combine -n LL1DScan${3} -M MultiDimFit --algo grid --points 100 --rMin 0.8 --rMax 1.2 ${1} ${safety} --expectSignal 1 ${2}
