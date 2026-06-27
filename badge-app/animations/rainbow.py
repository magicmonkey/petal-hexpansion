import asyncio

NAME = "Rainbows"

async def anim(petals):
    t1 = asyncio.create_task(outer_loop(petals))
    t2 = asyncio.create_task(middle_loop(petals))
    t3 = asyncio.create_task(inner_loop(petals))
    try:
        await asyncio.gather(t1, t2, t3)
    finally:
        t1.cancel()
        t2.cancel()
        t3.cancel()

async def outer_loop(petals):
    num_leds = 19
    tail_size = 10
    while True:
        for i in range(num_leds * 6):

            led = i % num_leds
            port = int(i/num_leds)
            petals.led_on(port, num_leds-1-led)

            i_off = i - tail_size
            if i_off < 0:
                i_off = (num_leds*6) + i_off
            led = i_off % num_leds
            port = int(i_off/num_leds)
            petals.led_off(port, num_leds-1-led)

            await asyncio.sleep_ms(20)

async def middle_loop(petals):
    num_leds =12 
    tail_size = 4
    offset = 19
    while True:
        for i in range(num_leds * 6):

            led = i % num_leds
            port = int(i/num_leds)
            petals.led_on(port, offset + num_leds-1 - led)

            i_off = i - tail_size
            if i_off < 0:
                i_off = (num_leds*6) + i_off
            led = i_off % num_leds
            port = int(i_off/num_leds)
            petals.led_off(port, offset + num_leds-1 - led)

            await asyncio.sleep_ms(20)

async def inner_loop(petals):
    num_leds = 5
    tail_size = 2
    offset = 19 + 12
    while True:
        for i in range(num_leds * 6):

            led = i % num_leds
            port = int(i/num_leds)
            petals.led_on(port, offset + num_leds-1 - led)

            i_off = i - tail_size
            if i_off < 0:
                i_off = (num_leds*6) + i_off
            led = i_off % num_leds
            port = int(i_off/num_leds)
            petals.led_off(port, offset + num_leds-1 - led)

            await asyncio.sleep_ms(20)
