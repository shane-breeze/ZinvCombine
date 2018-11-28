#!/bin/bash
safety="--robustFit 1 --rMin 0 --rMax 2"

nuisances=(prop_binmonojet_bin0 prop_binmonojet_bin1 prop_binmonojet_bin2 prop_binmonojet_bin3 prop_binmonojet_bin4 prop_binmonojet_bin5 prop_binmonojet_bin6 prop_binmonojet_bin7 prop_binmonojet_bin8 prop_binsinglemu_bin0 prop_binsinglemu_bin1 prop_binsinglemu_bin2 prop_binsinglemu_bin3 prop_binsinglemu_bin4 prop_binsinglemu_bin5 prop_binsinglemu_bin6 prop_binsinglemu_bin7 prop_binsinglemu_bin8 prop_bindoublemu_bin0 prop_bindoublemu_bin1 prop_bindoublemu_bin2 prop_bindoublemu_bin3 prop_bindoublemu_bin4 prop_bindoublemu_bin5 prop_bindoublemu_bin6 prop_bindoublemu_bin7 prop_bindoublemu_bin8 prop_binsingleele_bin0 prop_binsingleele_bin1 prop_binsingleele_bin2 prop_binsingleele_bin3 prop_binsingleele_bin4 prop_binsingleele_bin5 prop_binsingleele_bin6 prop_binsingleele_bin7 prop_binsingleele_bin8 prop_bindoubleele_bin0 prop_bindoubleele_bin1 prop_bindoubleele_bin2 prop_bindoubleele_bin3 prop_bindoubleele_bin4 prop_bindoubleele_bin5 prop_bindoubleele_bin6 prop_bindoubleele_bin7 prop_bindoubleele_bin8)
for nuis in ${nuisances[@]}; do
    combine -n "NuisFit${3}_${nuis}" -M MultiDimFit --algo impact --redefineSignalPOIs r -P ${nuis} --floatOtherPOIs 1 --saveInactivePOI 1 --expectSignal 1 ${safety} -d ${1} ${2}
done
