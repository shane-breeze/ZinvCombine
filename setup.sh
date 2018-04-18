#!/bin/bash
source /cvmfs/cms.cern.ch/cmsset_default.sh

if [ $(hostname -d) != hep.ph.ic.ac.uk ]; then
    echo "Only setup at Imperial so far"
    return
fi

export CMSSW_BASE="/vols/build/cms/sdb15/ZinvWidth/HiggsCombine/CMSSW_8_1_0"
cwd=$PWD
cd $CMSSW_BASE/src
cmsenv
cd $cwd
