import time

def anim(petals):
    for i in range(6):
        petals.led_outer_on(i)
        time.sleep_ms(1000)
        petals.led_outer_off(i)


