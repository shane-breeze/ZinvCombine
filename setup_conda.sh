#!/bin/bash
export TOPDIR=$PWD
source activate combine

export PYTHONPATH=$PYTHONPATH:$TOPDIR
export PATH=${PATH}:${TOPDIR}:${TOPDIR}/scripts
