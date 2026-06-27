import time

def anim(petals):
    petals.all_led_outer_on()
    time.sleep_ms(1000)
    petals.all_led_off()


