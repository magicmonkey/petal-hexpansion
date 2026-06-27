import asyncio

NAME = "Wheel"

async def anim(petals):
    while True:
        for i in range(6):
            petals.led_outer_on(i)
            await asyncio.sleep_ms(300)
            petals.led_outer_off(i)


