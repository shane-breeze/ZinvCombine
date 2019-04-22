#!/bin/bash
export TOPDIR=$PWD
conda activate combine

export PYTHONPATH=$PYTHONPATH:$TOPDIR
export PATH=${PATH}:${TOPDIR}:${TOPDIR}/scripts
