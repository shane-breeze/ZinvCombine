#!/bin/bash
safety="--robustFit 1 --rMin 0.5 --rMax 1.5"
combine -n "NominalFit${3}" -M MultiDimFit --algo singles --redefineSignalPOIs r --expectSignal 1 ${safety} -d ${1} ${2}

nuisances=$(cat ${1/root/txt} | awk '{print $1}' | sed -e '1,/rate/d' | tail -n +2 | sed -e '/-----/,$d')
for nuis in ${nuisances[@]}; do
    combine -n "NuisFit${3}_${nuis}" -M MultiDimFit --algo impact --redefineSignalPOIs r -P ${nuis} --floatOtherPOIs 1 --saveInactivePOI 1 --expectSignal 1 ${safety} -d ${1} ${2}
done

combine -n "NuisFit${3}_stat" -M MultiDimFit --algo singles --freezeParameters all --expectSignal 1 ${safety} ${1} ${2}
