import RPi.GPIO as GPIO
import time

# Pin Definitions
input_pin = 5  # BCM pin 18, BOARD pin 12
output_pin = 5


def main():
    prev_value = None

    # Pin Setup:
    GPIO.setmode(GPIO.BCM)  # BCM pin-numbering scheme from Raspberry Pi
    GPIO.setup(input_pin, GPIO.IN)  # set pin as an input pin

    GPIO.setup(output_pin, GPIO.OUT, initial=GPIO.HIGH)
    curr_value = GPIO.LOW

    print("Starting demo now! Press CTRL+C to exit")
    try:
        while True:
            value = GPIO.input(input_pin)
            print('第1',value)
            if value != prev_value:
                if value == GPIO.HIGH:
                    value_str = "HIGH"
                else:
                    value_str = "LOW"
                print("Value read from pin {} : {}".format(input_pin,
                                                           value_str))
            time.sleep(1)
            
            GPIO.output(output_pin, curr_value)
            value2 = GPIO.input(input_pin)
            print('第2',value2)
    finally:
        GPIO.cleanup()

if __name__ == '__main__':
    main()
