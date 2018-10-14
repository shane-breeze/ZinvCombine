#!/bin/bash
add_opt="-t -1"
combine -n "MLFit" ${1} -M FitDiagnostics --saveNLL --plots --saveNormalizations --saveWithUncertainties --expectSignal 1 ${add_opt}
