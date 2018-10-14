#!/bin/bash
add_opt=""
text2workspace.py ${1} --channel-masks
combine -n "MLFitMasked" -M FitDiagnostics --saveShapes --saveNorm --saveWithUncert ${1/txt/root} --setParameters mask_monojet=1,mask_doublemu=1 --keepFailures ${add_opt}
