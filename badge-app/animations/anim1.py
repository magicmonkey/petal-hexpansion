import asyncio

NAME = "Simple"

async def anim(petals):
    petals.all_led_outer_on()
    await asyncio.sleep_ms(1000)
    petals.all_led_off()


