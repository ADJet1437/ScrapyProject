#!/usr/bin/env bash

pushd `dirname $0` > /dev/null
PROJECT_PATH=`pwd -P`
popd > /dev/null

cd $PROJECT_PATH

if [ $(hg branch) != develop ]
then
    echo "Current branch is not develop"
    exit 1
fi

hg summary --remote | grep -q 'remote: (synced)' ; echo $?

if [ $? -ne 0 ]
then
    echo "There are unpushed changes"
    exit 1
fi

if [ $(hg status -m -a -r -d | wc -l) -ne 0 ]
then
    echo "Uncommited changes exist."
    exit 1
fi

hg up default
hg merge develop
hg commit -m "release to default"
hg push
hg up develop