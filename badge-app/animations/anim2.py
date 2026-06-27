import time

NAME = "Continuous"

def anim(petals):
    for i in range(10):
        for i in range(6):
            petals.led_outer_on(i)
            time.sleep_ms(300)
            petals.led_outer_off(i)


