import asyncio
import random

NAME = "Confetti"

INNER_BAND_COUNT = 5
MIDDLE_BAND_COUNT = 12
OUTER_BAND_COUNT = 19

band_count = {
    0: OUTER_BAND_COUNT,
    1: MIDDLE_BAND_COUNT,
    2: INNER_BAND_COUNT,
}

band_offset = {
    0: 0,
    1: OUTER_BAND_COUNT,
    2: OUTER_BAND_COUNT + MIDDLE_BAND_COUNT,
}

active_leds = {}

async def anim(petals):
    # clean sheet to start
    petals.all_led_off()

    # main loop
    while(True):
        await asyncio.sleep_ms(100)
        led_random(petals)
        decay(petals)

def led_random(petals):
    # pick a band (outer, middle, inner)
    band = random.randint(0,2)
    # pick an LED
    led = random.randint(0, band_count[band] - 1) + band_offset[band]

    # turn on the LED and add to the list
    petals.one_led_on(led)
    active_leds[led] = 5 + random.randint(0, 10) # TTL

def decay(petals):
    # reduce TTL, turn off and delist if zero
    for led in list(active_leds):
        active_leds[led] -= 1
        if active_leds[led] < 1:
            del active_leds[led]
            petals.one_led_off(led)

