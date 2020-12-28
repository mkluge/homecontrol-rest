#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time

# Import the ADS1115 module.
from ADS1x15 import ADS1115
adc = ADS1115()

# Start continuous ADC conversions on channel 0
adc.start_adc(0, gain=1)

# 10 Sekunden lang Daten lesen
start = time.time()
while (time.time() - start) <= 10.0:
    # Read the last ADC conversion value and print it out.
    value = adc.get_last_result()
    print('%d - %.5f V' % (value, float(value)*4.096/32768.0))
    # Sleep for half a second.
    time.sleep(0.5)
adc.stop_adc()
