#!/usr/bin/env bash

myWorkDir="$PWD"
myName=$(basename "$0")
myFullName=$(readlink -f "$0") # canonicalized path
myBinDir=$(dirname "$myFullName") # canonicalized path

colorBlack='\033[0;30m'
colorRed='\033[0;31m'
colorGreen='\033[0;32m'
colorBrown='\033[0;33m'
colorOrange='\033[0;33m'
colorBlue='\033[0;34m'
colorPurple='\033[0;35m'
colorCyan='\033[0;36m'
colorLightGray='\033[0;37m'
colorDarkGray='\033[1;30m'
colorLightRed='\033[1;31m'
colorLightGreen='\033[1;32m'
colorYellow='\033[1;33m'
colorLightBlue='\033[1;34m'
colorLightPurple='\033[1;35m'
colorLightCyan='\033[1;36m'
colorWhite='\033[1;37m'
colorNone='\033[0m' # No color

formsSeparator=$'\n'
formsTitle="Change FOOBAR password "
formsText="Details... "
formsPassword1FieldName='(current) FOOBAR password'
formsPassword2FieldName='Enter new FOOBAR password'
formsPassword3FieldName='Retype new FOOBAR password'
formsDataLen=3

allZenityOpts=(
    --calendar
    --entry
    --error
    --info
    --file-selection
    --list
    --notification
    --progress
    --question
    --warning
    --scale
    --text-info
    --color-selection
    --password
    --forms
)

knownZenityOpts=(
    error
    info
    question
    warning
    forms
)
#knownZenityOpts+=(entry)
#knownZenityOpts+=(password)

#for opt in "${allZenityOpts[@]}"; do
#    echo -e "${colorPurple}zenity ${opt}${colorNone}"
#    zenity ${opt}
#done
#for opt in "${knownZenityOpts[@]}"; do
#    echo -e "${colorPurple}zenity --${opt}${colorNone}"
#    zenity --${opt}
#    if [[ $? == 0 ]]; then
#        echo -e "${colorGreen}exit ${?}${colorNone}"
#    else
#        echo -e "${colorRed}exit ${?}${colorNone}"
#    fi
#done
for opt in "${knownZenityOpts[@]}"; do
    for bin in "${myBinDir}/python2/pyzano_gtk2.py" "${myBinDir}/python3/pyzano_gtk3.py"; do
        echo -e "${colorPurple}'${bin}' ${opt}${colorNone}"
        "${bin}" ${opt}
        if [[ $? == 0 ]]; then
            echo -e "${colorGreen}exit ${?}${colorNone}"
        else
            echo -e "${colorRed}exit ${?}${colorNone}"
        fi
    done
done

#echo -e "${colorBlue}zenity --forms ...${colorNone}"
#zenity --forms \
#    --separator="$formsSeparator" \
#    --add-password="$formsPassword1FieldName" \
#    --add-password="$formsPassword2FieldName" \
#    --add-password="$formsPassword3FieldName" \
#    --title="$formsTitle" --text="$formsText"
#if [[ $? == 0 ]]; then
#    echo -e "${colorGreen}exit ${?}${colorNone}"
#else
#    echo -e "${colorRed}exit ${?}${colorNone}"
#fi
for bin in "${myBinDir}/python2/pyzano_gtk2.py" "${myBinDir}/python3/pyzano_gtk3.py"; do
    echo -e "${colorPurple}'${bin}' forms ...${colorNone}"
    "${bin}" forms \
        --separator="$formsSeparator" \
        --add-password="$formsPassword1FieldName" \
        --add-password="$formsPassword2FieldName" \
        --add-password="$formsPassword3FieldName" \
        --title="$formsTitle" --text="$formsText"
    if [[ $? == 0 ]]; then
        echo -e "${colorGreen}exit ${?}${colorNone}"
    else
        echo -e "${colorRed}exit ${?}${colorNone}"
    fi
done
