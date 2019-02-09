#!/bin/bash
combine -M MultiDimFit ${1} --algo none --expectSignal 1 --robustFit 1 --rMin 0.5 --rMax 1.5 --saveFitResult --saveWorkspace ${2} -n ${3}
PostFitShapesFromWorkspace -w higgsCombine${3}.MultiDimFit.mH120.root -o test.root --postfit 1 -f multidimfit${3}.root:fit_mdf --sampling --print
