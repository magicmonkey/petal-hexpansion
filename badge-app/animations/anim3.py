import asyncio

NAME = "Continuous"

async def anim(petals):
    while True:
        for i in range(6):
            petals.led_outer_on(i)
            petals.led_middle_on(5-i)
            await asyncio.sleep_ms(300)
            petals.led_middle_off(5-i)
            petals.led_outer_off(i)


