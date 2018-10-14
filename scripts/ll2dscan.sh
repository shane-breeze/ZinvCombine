#!/bin/bash
add_opt="-t -1"
text2workspace.py -P HiggsAnalysis.CombinedLimit.PhysicsModel:multiSignalModel --PO 'map=.*/znunu:r_nunu[1,0,10]' --PO 'map=.*/zmumu:r_mumu[1,0,10]' ${1} --PO verbose

combine -n LL2DScan -M MultiDimFit --algo grid --points 14400 --setParameterRanges r_nunu=0.7,1.3:r_mumu=0.7,1.3 --setParameters r_mumu=1,r_nunu=1 ${1/txt/root} --robustFit 1 ${add_opt}
combine -n LL2DCont68 -M MultiDimFit --algo contour2d --points 100 --cl=0.68 --setParameters r_mumu=1,r_nunu=1 ${1/txt/root} --robustFit 1 ${add_opt}
combine -n LL2DCont95 -M MultiDimFit --algo contour2d --points 100 --cl=0.95 --setParameters r_mumu=1,r_nunu=1 ${1/txt/root} --robustFit 1 ${add_opt}
