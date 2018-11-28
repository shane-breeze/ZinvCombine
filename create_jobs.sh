#!/bin/bash
script=${1}
direc=${2}
addopts=${3}
name=${4}

datacard="datacard.txt"
if [[ "$script" == "ll2dscan.sh" ]]; then
    datacard="datacard_2d.txt"
fi

i=0
for dc in ${direc}/*/${datacard}; do
    echo $dc
    filename="job_${script/\.sh/}_${i}.sh"

    workingdir=$(dirname ${dc})
    workingdir=$(realpath ${workingdir})

    echo "#!/bin/bash" > $filename
    echo "cd ${workingdir}" >> $filename
    echo "${script} ${datacard} \"${addopts}\" \"${name}\"" >> $filename

    i=$((i+1))
done
