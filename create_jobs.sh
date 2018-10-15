#!/bin/bash
script=${1}
direc=${2}
addopts=${3}
name=${4}

i=0
for dc in ${direc}/*/datacard.txt; do
    filename="job${i}.sh"

    workingdir=$(dirname ${dc})
    workingdir=$(realpath ${workingdir})

    echo "#!/bin/bash" > $filename
    echo "cd ${workingdir}" >> $filename
    echo "${script} datacard.txt \"${addopts}\" \"${name}\"" >> $filename

    i=$((i+1))
done
