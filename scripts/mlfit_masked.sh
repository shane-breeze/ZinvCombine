#!/bin/bash
combine -n Zinv -m 91 -M FitDiagnostics --saveShapes --saveNorm --saveWithUncert ${1} --setParameters mask_monojet=1 --keepFailures
