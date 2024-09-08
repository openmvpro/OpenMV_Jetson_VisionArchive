
import sensor, image, time, math
from pyb import UART
from pyb import LED

# LED灯定义
red_led    = LED(1)
green_led  = LED(2)
blue_led   = LED(3)


sensor.reset()
sensor.set_pixformat(sensor.GRAYSCALE)
sensor.set_framesize(sensor.VGA) # High Res!
#sensor.set_windowing((160, 80)) # V Res of 80 == less work (40 for 2X the speed).
sensor.skip_frames(time = 2000)
sensor.set_auto_gain(False)  # must turn this off to prevent image washout...
sensor.set_auto_whitebal(False)  # must turn this off to prevent image washout...
clock = time.clock()



#EAN
#CODE128
#UPC-A
#CODE39
#ITF14
#MSI
#CODABAR


def barcode_name(code):

    if(code.type() == image.EAN2):

        return "EAN2"

    if(code.type() == image.EAN5):

        return "EAN5"

    if(code.type() == image.EAN8):

        return "EAN8"

    if(code.type() == image.UPCE):

        return "UPCE"

    if(code.type() == image.ISBN10):

        return "ISBN10"

    if(code.type() == image.UPCA):

        return "UPCA"

    if(code.type() == image.EAN13):

        return "EAN13"

    if(code.type() == image.ISBN13):

        return "ISBN13"

    if(code.type() == image.I25):

        return "I25"

    if(code.type() == image.DATABAR):

        return "DATABAR"

    if(code.type() == image.DATABAR_EXP):

        return "DATABAR_EXP"

    if(code.type() == image.CODABAR):

        return "CODABAR"

    if(code.type() == image.CODE39):

        return "CODE39"

    if(code.type() == image.PDF417):

        return "PDF417"

    if(code.type() == image.CODE93):

        return "CODE93"

    if(code.type() == image.CODE128):

        return "CODE128"

i = 0
while(True):

    clock.tick()

    img = sensor.snapshot()

    codes = img.find_barcodes()

    if codes:
        for code in codes:
            img.draw_rectangle(code.rect())

            print_args = (barcode_name(code), code.payload(), (180 * code.rotation()) / math.pi, code.quality(), clock.fps())
            print("Barcode %s, Payload \"%s\", rotation %f (degrees), quality %d, FPS %f" % print_args)



    red_led.on()
    green_led.on()
    blue_led.on()
    pass
