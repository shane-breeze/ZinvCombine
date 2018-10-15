#!/bin/bash
for job in job*.sh; do
    qsub -cwd -V -q hep.q -l h_rt=0:30:0 ${job}
done
