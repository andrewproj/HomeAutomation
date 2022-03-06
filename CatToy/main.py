from time import sleep
from gpiozero.pins.pigpio import PiGPIOFactory
from gpiozero import Servo, MotionSensor, Device


def run_cat_toy():
    factory = PiGPIOFactory(host='cattoy')
    Device.pin_factory = factory

    #servo = Servo(pin=13, min_pulse_width=0.8/1000, max_pulse_width=2.2/1000)
    # while True:
    #     servo.min()
    #     sleep(1)
    #     servo.max()
    #     sleep(1)

    # pir = MotionSensor(pin=26)
    # while True:
    #     pir.wait_for_motion(1)
    #     if pir.motion_detected:
    #         print("Motion detected!")
    #         pir.wait_for_no_motion(timeout=5)
    #     else:
    #         print(".")
    #     sleep(.5)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    run_cat_toy()
