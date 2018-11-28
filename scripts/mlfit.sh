#!/bin/bash
safety="--robustFit 1 --rMin 0 --rMax 2"
combine -n MLFit${3} ${1} -M FitDiagnostics --saveShapes --saveWithUncertainties ${safety} --expectSignal 1 ${2}
