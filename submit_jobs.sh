#!/bin/bash
for job in job_${1}_*.sh; do
    qsub -cwd -V -q hep.q -l h_rt=1:0:0 ${job}
done
