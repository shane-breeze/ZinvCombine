#!/bin/bash
safety="--robustFit 1 --rMin 0 --rMax 2"
combine -n LL2DScan${3} -M MultiDimFit --algo grid --points 57600 --setParameterRanges r_nunu=0.7,1.3:r_mumu=0.7,1.3 ${1/txt/root} ${safety} ${2}
combine -n LL2DCont68${3} -M MultiDimFit --algo contour2d --points 100 --cl=0.68 ${1/txt/root} ${safety} ${2}
combine -n LL2DCont95${3} -M MultiDimFit --algo contour2d --points 100 --cl=0.95 ${1/txt/root} ${safety} ${2}
