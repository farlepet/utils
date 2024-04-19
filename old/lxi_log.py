#!/bin/python3
# Usage:
#  lxi_log.py <ip addr> <duration> <log file>

import sys, time
import vxi11

# Put these constants here just to avoid having a bajillion command-line
# arguments. Ideally we'd have defaults then set them to other values via flags.
dataRate  = 1000. # Data rate in Hz
precision = 1.
buffSize  = 5000 # Buffer size in points
measFunc  = "CURRent"
readSize  = 1000


def main():
    devip    = sys.argv[1]
    duration = int(sys.argv[2])
    logfile  = sys.argv[3]

    dev = vxi11.Instrument(devip)
    if(dev == None):
        print("Could not instantiate VXI11 Instrument!")

    log = open(logfile, "w")

    # Reset to known state
    dev.clear()
    dev.write('*RST')

    print("Identity: " + dev.ask("*IDN?"))


    #
    # Setup input
    #
    dev.write(f':FUNCtion "{measFunc}"')
    dev.write(f':SENS:{measFunc}:RANGe:AUTO OFF')
    dev.write(f':SENS:{measFunc}:RANGe 1')

    #dev.write(':SENS:CURRent:NPLCycles 1')
    dev.write(f':SENS:{measFunc}:APERture {1 / dataRate}')
    

    #
    # Setup reading buffers:
    #

    # Clear default buffers:
    dev.write('TRACe:CLEar "defbuffer1"')
    dev.write('TRACe:CLEar "defbuffer2"')
    # Set buffer size
    dev.write(f'TRACe:POINts {buffSize},"defbuffer1"')
    dev.write(f'TRACe:POINts {buffSize},"defbuffer2"')
    # Set fill mode
    dev.write('TRACe:FILL:MODE ONCE,"defbuffer1"')
    dev.write('TRACe:FILL:MODE ONCE,"defbuffer2"')

    # Log data
    totalPoints = dataRate * duration
    bufferTime  = 4 * buffSize / dataRate
    pointsSoFar = 0
    cBuffer = 1
    
    # Start logging
    dev.write(f'TRIGger:LOAD "DurationLoop", {bufferTime}, 0, "defbuffer1"')
    dev.write('INIT')    

    while pointsSoFar < totalPoints:
        buffPoints = int(dev.ask(f'TRACe:ACTual? "defbuffer{cBuffer}"'))
        print(f'Points[{cBuffer}]: {buffPoints}')

        if buffPoints > (buffSize * 0.5):
            # Swap current buffer
            oBuffer = cBuffer
            cBuffer = 1 if (cBuffer == 2) else 2

            # Switch trigger to other buffer
            dev.write('ABORt')
            dev.write(f'TRIGger:LOAD "Empty"')
            dev.write(f'TRIGger:LOAD "DurationLoop", {bufferTime}, 0, "defbuffer{cBuffer}"')
            dev.write('INIT')
            dev.write(f'DISPlay:BUFFer:ACTive "defbuffer{cBuffer}"')

            # Dump contents of buffer
            buffPoints = int(dev.ask(f'TRACe:ACTual? "defbuffer{oBuffer}"'))
            pointsSoFar += buffPoints
            offset = 1
            while buffPoints > 0:
                toRead = readSize if buffPoints > readSize else buffPoints
                points = dev.ask(f':TRACe:DATA? {offset},{offset+toRead-1},"defbuffer{oBuffer}",SEC,FRAC,READ')
                log.write(points)
                offset += toRead
                buffPoints -= toRead
            
            dev.write(f'TRACe:CLEar "defbuffer{oBuffer}"')

        time.sleep(0.5)
    

if __name__ == '__main__':
    main()
