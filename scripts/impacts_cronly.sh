#!/bin/bash
safety="--robustFit 1"
parameters="--redefineSignalPOIs tf_wlnu --setParameters r=1,r_z=1,mask_monojet=1,mask_doublemu=1,mask_singleele=1,mask_doubleele=1 --freezeParameters r,r_z"
combine -n "CROnlyNominalFit${3}" -M MultiDimFit --algo singles ${parameters} ${safety} -d ${1} ${2}

nuisances=$(cat ${1/root/txt} | awk '{print $1}' | sed -e '1,/rate/d' | tail -n +2 | sed -e '/-----/,$d')
for nuis in ${nuisances[@]}; do
    combine -n "CROnlyNuisFit${3}_${nuis}" -M MultiDimFit --algo impact ${parameters} -P ${nuis} --floatOtherPOIs 1 --saveInactivePOI 1 ${safety} -d ${1} ${2}
done
