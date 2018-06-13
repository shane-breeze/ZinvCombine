#!/bin/bash
#combine -M MultiDimFit --algo grid --points 251001 --setParameterRanges r_nunu=0.6,1.4:r_mumu=0.6,1.4 -m 91 ${1}
draw_ll2dscan.py ${PWD}/higgsCombineTest.MultiDimFit.mH91.root ${PWD}/ll2dscan.pdf -x r_mumu -y r_nunu -n 250 --x-range "(0.8,1.2)" --y-range "(0.9,1.3)"
