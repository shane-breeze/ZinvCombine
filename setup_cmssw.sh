#!/bin/bash
export cwd="$PWD"
export CMSSW_BASE="/vols/build/cms/sdb15/ZinvWidth/HiggsCombine/CMSSW_8_1_0"
export PYTHON_EXTRA="/home/hep/sdb15/externals"

source /cvmfs/cms.cern.ch/cmsset_default.sh

if [ $(hostname -d) != hep.ph.ic.ac.uk ]; then
    echo "Only setup at Imperial so far"
    return
fi

cd $CMSSW_BASE/src
eval `scramv1 runtime -sh`
cd $cwd

export PATH=${PATH}:${cwd}:${cwd}/scripts
export PYTHONPATH=${PYTHONPATH}:${cwd}
