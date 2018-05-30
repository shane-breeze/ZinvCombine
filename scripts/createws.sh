#!/bin/bash
text2workspace.py -m 91 -P HiggsAnalysis.CombinedLimit.PhysicsModel:multiSignalModel --PO 'map=.*/znunu:r_nunu[1,0,10]' --PO 'map=.*/dymumu:r_mumu[1,0,10]' ${1} --PO verbose
