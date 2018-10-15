#!/bin/bash
text2workspace.py -P HiggsAnalysis.CombinedLimit.PhysicsModel:multiSignalModel --PO 'map=.*/znunu:r_nunu[1,0,10]' --PO 'map=.*/zmumu:r_mumu[1,0,10]' ${1} --PO verbose

safety="--robustFit 1 --rMin 0 --rMax 5"
combine -n LL2DScan${3} -M MultiDimFit --algo grid --points 57600 --setParameterRanges r_nunu=0.7,1.3:r_mumu=0.7,1.3 --setParameters r_mumu=1,r_nunu=1 ${1/txt/root} ${safety} ${2}
combine -n LL2DCont68${3} -M MultiDimFit --algo contour2d --points 100 --cl=0.68 --setParameters r_mumu=1,r_nunu=1 ${1/txt/root} ${safety} ${2}
combine -n LL2DCont95${3} -M MultiDimFit --algo contour2d --points 100 --cl=0.95 --setParameters r_mumu=1,r_nunu=1 ${1/txt/root} ${safety} ${2}
