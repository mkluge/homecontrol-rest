#!/bin/bash
for I in `seq 1 50` ; do /usr/bin/irsend --device=/var/run/lirc/lircd-tx SEND_ONCE EPSON-TW6000 $1 ; done
