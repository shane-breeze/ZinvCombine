#!/bin/bash

## Systematic impacts
combineTool.py -M Impacts -d ${1} -m 91 --doInitialFit
combineTool.py -M Impacts -d ${1} -m 91 --doFits
combineTool.py -M Impacts -d ${1} -m 91 -o impacts.json
plotImpacts.py -i impacts.json -o impacts

## Stats impacts
combine ${1} -n StatsImpacts -m 91 -M FitDiagnostics --forceRecreateNLL --freezeParameters all
fitdiag_to_fitparams.py fitDiagnosticsStatsImpacts.root -o impacts_stats.json

merge_impact_jsons.py impacts.json impacts_stats.json -o impacts.json
