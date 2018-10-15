#!/bin/bash
text2workspace.py ${1} --channel-masks

safety="--robustFit 1 --rMin 0 --rMax 5"
combine -n "MLFitMasked${3}" -M FitDiagnostics --saveShapes --saveNorm --saveWithUncert ${1/txt/root} --setParameters mask_monojet=1,mask_doublemu=1 ${safety} --keepFailures ${2}
