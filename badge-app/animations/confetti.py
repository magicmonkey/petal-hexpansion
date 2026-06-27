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

async def anim(petals):
    petals.all_led_off()
    for i in range(50):
        await asyncio.sleep_ms(100)
        led_random(petals)

def led_random(petals):
    # pick a band (outer, middle, inner)
    band = random.randint(0,2)
    # pick an LED
    led = random.randint(0, band_count[band] - 1) + band_offset[band]
    print("LED: " + str(led))
    petals.one_led_on(led)


