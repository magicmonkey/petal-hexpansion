import asyncio

NAME = "Dual wheel"

async def anim(petals):
    # Run 2 async loops underneath this one
    t1 = asyncio.create_task(outer_loop(petals))
    await asyncio.sleep_ms(150)
    t2 = asyncio.create_task(middle_loop(petals))
    try:
        await asyncio.gather(t1, t2)
    finally:
        t1.cancel()
        t2.cancel()

async def outer_loop(petals):
    while True:
        for i in range(6):
            petals.led_outer_on(i)
            await asyncio.sleep_ms(450)
            petals.led_outer_off(i)

async def middle_loop(petals):
    while True:
        for i in range(6):
            petals.led_middle_on(5-i)
            await asyncio.sleep_ms(210)
            petals.led_middle_off(5-i)
