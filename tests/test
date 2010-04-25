#!/bin/sh
if [ $# -lt 1 ]
then
    echo "Usage: $0 <file>"
    exit
fi
objdump -x $1 | awk '/^ [0-9]* .text/{textvirt=strtonum("0x" $4); textstart=strtonum("0x" $6); textlen=$3} /main$/{mainvirt=strtonum("0x" $1); main=textstart+mainvirt-textvirt; printf "%x %s\n", main, $(NF-1)}' | xargs ../ocd.py $1
