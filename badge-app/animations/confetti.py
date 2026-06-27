import time
import random

def anim(petals):
    for i in range(50):
        time.sleep_ms(100)
        led_random(petals)


def led_random(petals):
    # pick an LED
    led = random.randint(0, 35)
    print("LED: " + str(led))
    petals.one_led_on(led)


