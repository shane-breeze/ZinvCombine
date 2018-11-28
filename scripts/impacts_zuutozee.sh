#!/bin/bash
safety="--robustFit 1"
parameters="--setParameters mask_monojet=1,mask_singlemu=1,mask_singleele=1,tf_wlnu=1 --freezeParameters tf_wlnu --expectSignal 1"
combine -n "ZuuToZeeNominalFit${3}" -M MultiDimFit --algo singles ${parameters} ${safety} -d ${1} ${2}

nuisances=$(cat ${1/root/txt} | awk '{print $1}' | sed -e '1,/rate/d' | tail -n +2 | sed -e '/-----/,$d')
for nuis in ${nuisances[@]}; do
    combine -n "ZuuToZeeNuisFit${3}_${nuis}" -M MultiDimFit --algo impact ${parameters} -P ${nuis} --floatOtherPOIs 1 --saveInactivePOI 1 ${safety} -d ${1} ${2}
done
