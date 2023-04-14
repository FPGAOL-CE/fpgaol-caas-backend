#!/bin/bash
# File              : compile.openxc7.sh
# License           : GPL-3.0-or-later
# Author            : Peter Gu <github.com/regymm>
# Date              : 2023.04.14
# Last Modified Date: 2023.04.14

if [[ "$UID" != "0" ]]; then
	echo 'This should run in Docker as root!'
	exit 1
fi

source /prjxray/env/bin/activate

cp -a /mnt/* /tmp
make -C /tmp

retval=$?

cp /tmp/top.log /mnt


# a hack to check if OOM-ed
grep -E '(Killed|KILL)' /tmp/top.log && exit 233

if [[ "$retval" == "0" ]]; then
    cp /tmp/top.bit /mnt
	exit 0
else
	exit 1
fi
