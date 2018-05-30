#!/bin/bash
combineTool.py -M Impacts -d ${1} -m 91 --doInitialFit
combineTool.py -M Impacts -d ${1} -m 91 --doFits
combineTool.py -M Impacts -d ${1} -m 91 -o impacts.json
plotImpacts.py -i impacts.json -o impacts
