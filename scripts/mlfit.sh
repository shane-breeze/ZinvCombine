#!/bin/bash
safety="--robustFit 1 --rMin 0 --rMax 5"
combine -n MLFit${3} ${1} -M FitDiagnostics --saveNLL --plots --saveNormalizations --saveWithUncertainties ${safety} --expectSignal 1 ${2}
