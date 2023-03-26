#!/bin/bash
# File              : compile.sh
# License           : GPL-3.0-or-later
# Author            : Peter Gu <github.com/regymm>
# Date              : 2023.03.25
# Last Modified Date: 2023.03.26

if [[ "$UID" != "0" ]]; then
	echo 'This should run in Docker as root!'
	exit 1
fi

source /opt/conda/etc/profile.d/conda.sh
conda activate xc7
cp -a /mnt/* /tmp
make -C /tmp

if [[ "$?" == "0" ]]; then
	cp /tmp/build/top.bit /mnt
	cp /tmp/build/top.log /mnt
	exit 0
else
	cp /tmp/build/top.log /mnt
	exit 1
fi
