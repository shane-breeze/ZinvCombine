#!/bin/bash
add_opt="-t -1"
combine -n LL1DScan -M MultiDimFit --algo grid --points 100 --rMin 0.8 --rMax 1.2 ${1} -m 91 --expectSignal 1 ${add_opt}
