#!/bin/bash
add_opts="-t -1"

combine -n "NominalFit" -M MultiDimFit --algo singles --redefineSignalPOIs r --expectSignal 1 --robustFit 1 -d ${1} ${add_opts}

for nuis in jer jes lumi metTrigSF muonId muonIso muonTrack pileup unclust; do
    combine -n "NuisFit_${nuis}" -M MultiDimFit --algo impact --redefineSignalPOIs r -P ${nuis} --floatOtherPOIs 1 --saveInactivePOI 1 --expectSignal 1 --robustFit 1 -d ${1} ${add_opts}
done

combine -n "NuisFit_statg" -M FitDiagnostics --expectSignal 1 --robustFit 1 --freezeParameters all ${1} ${add_opts}
