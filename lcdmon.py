#! /usr/bin/env python3
#
import smbus
import sys
import os
import time
import lcd_i2c as lcd

LCKF = "/tmp/lcdmon.lck"
TXTF = "/tmp/lcdmon.dat"
ADDR = 0x3f
bus  = smbus.SMBus(0)

while(1):
    try:
        dummy = bus.read_byte(ADDR)
    except OSError:
        if os.path.exists(LCKF):
            os.unlink(LCKF)
        time.sleep(0.1)
        continue
    except KeyboardInterrupt:
        os.unlink(LCKF)
        exit()

    if os.path.exists(LCKF):
        pass
    else:
        lcd.lcd_init()
        f = open(LCKF,"w")
        f.write(" ")
        f.close()
        f = open(TXTF,"w")
        f.write("-1,-1,home")
        f.close()

    try:
        with open(TXTF) as f:
            for rdata in f:
                (x,y,t0) = rdata.split(',')
                t = t0.rstrip()
                if (x=="-1"):  # COMMAND
                    if (t=="home"):
                        lcd.home()
                    elif (t=="clear"):
                        lcd.clear()
                else:
                    lcd.setCursor(int(x),int(y))
                    lcd.print(t)
            os.unlink(TXTF)
    except:
        pass
