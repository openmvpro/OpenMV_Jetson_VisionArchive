'''import time
from pyb import UART

uart = UART(3, 115200)

while(True):
    uart.write("Hello World!\r")
    time.sleep(1000)

import struct

data=struct.pack("BBiiiBB",
                 0XAA,
                 0XAE,
                 1,
                 2,
                 3,
                 0X0D,
                 0X0A)
print(data)
print(struct.unpack("BBiiiBB",data))
'''

import time
from pyb import UART
import struct


uart = UART(3, 115200)

while(True):
    if uart.any():
        a = uart.read(2)
        print(a)
        if a == b'\r\n':
            b = uart.read(16)
            print(b)
            if b != None:
                c=struct.unpack("<BBiiiBB",b)
                print(c)
                uart.write(b)



