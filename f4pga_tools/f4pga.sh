#!/bin/bash -ex
# File              : f4pga.sh
# License           : GPL-3.0-or-later
# Author            : Peter Gu <github.com/regymm>
# Date              : 2023.03.25
# Last Modified Date: 2023.03.25

workroot=$1
simplejob=$2
device=$3
xdcfile=$4
srcfile1=$5

if [[ "$simplejob" != "1" ]]; then
	echo 'Only simple job is support now!'
	exit 1
fi

cp -v f4pga_tools/Makefile $workroot/
docker run -it --rm \
	-v `pwd`/$workroot:/mnt \
	-e TOP=top \
	-e XDC=/tmp/$xdcfile \
	-e SOURCES=/tmp/$srcfile1 \
	-e BUILDDIR=/tmp/build \
	--tmpfs /tmp \
	carlosedp/symbiflow bash -c "source /opt/conda/etc/profile.d/conda.sh && conda activate xc7 && cp -a /mnt/* /tmp && make -C /tmp && cp /tmp/build/top.bit /mnt"
