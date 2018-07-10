#!/bin/bash
combine -M MultiDimFit --algo grid --points 25921 --setParameterRanges r_nunu=0.8,1.2:r_mumu=0.8,1.2 -m 91 -t -1 --setParameters r_mumu=1,r_nunu=1 ${1}
mv higgsCombineTest.MultiDimFit.mH91.root multidimfit_rmumurnunu_gridscan.root
combine -M MultiDimFit --algo contour2d --points 100 -m 91 --cl=0.68 -t -1 --setParameters r_mumu=1,r_nunu=1 ${1}
mv higgsCombineTest.MultiDimFit.mH91.root multidimfit_rmumurnunu_contour2d_cl68.root
combine -M MultiDimFit --algo contour2d --points 100 -m 91 --cl=0.95 -t -1 --setParameters r_mumu=1,r_nunu=1 ${1}
mv higgsCombineTest.MultiDimFit.mH91.root multidimfit_rmumurnunu_contour2d_cl95.root
draw_ll2dscan.py multidimfit_rmumurnunu_gridscan.root:multidimfit_rmumurnunu_contour2d_cl68.root:multidimfit_rmumurnunu_contour2d_cl95.root ${PWD}/ll2dscan.pdf -x r_mumu -y r_nunu -n 160 --x-range "(0.8,1.2)" --y-range "(0.8,1.2)"
