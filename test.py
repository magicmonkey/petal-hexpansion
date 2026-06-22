import asyncio

from app import App
from events.input import Buttons, BUTTON_TYPES
from system.hexpansion.config import HexpansionConfig
import time

AL5887 = 0x30
PORT = 4

# Need to re-map the LEDs because they're wired up weirdly to the chip
# This happens _after_ any other LED-based modifiers
led_map = [
    # Outer band, first half
    0, 1, 2, 3, 4, 5, 6, 7, 8, 9,
    # Outer band, second half
    27, 28, 29, 30, 31, 32, 33, 34, 35,
    # Middle band, first half
    10, 11, 12, 13, 14, 15,
    # Middle band, second half
    21, 22, 23, 24, 25, 26,
    # Inner band, first half
    16, 17, 18,
    # Inner band, second half
    19, 20,
]

OUTER  = 2
MIDDLE = 64
INNER  = 2

led_brightness = [
    OUTER, OUTER, OUTER, OUTER, OUTER, OUTER, OUTER, OUTER, OUTER, OUTER, OUTER, OUTER, OUTER, OUTER, OUTER, OUTER, OUTER, OUTER, OUTER, 
    MIDDLE, MIDDLE, MIDDLE, MIDDLE, MIDDLE, MIDDLE, MIDDLE, MIDDLE, MIDDLE, MIDDLE, MIDDLE, MIDDLE, 
    INNER, INNER, INNER, INNER, INNER, 
]

have_petals = [
    False,
    False,
    False,
    False,
    False,
    False,
]

class PetalTestApp(App):
    def __init__(self):
        self.config = HexpansionConfig(PORT)
        self.i2c_devices = []
        self.ls_c_value = None
        self.button_states = Buttons(self)
        self._setup_pins()
        super().__init__()

    def _setup_pins(self):
        ls_a, ls_b, ls_c = self.config.ls_pin[0], self.config.ls_pin[1], self.config.ls_pin[2]
        ls_c.init(ls_c.IN)
        ls_b.init(ls_b.OUT)
        ls_b.off()        # RSTn LOW: assert hardware reset
        ls_a.init(ls_a.OUT)
        ls_a.off()        # EN LOW: disable during reset
        time.sleep_ms(10)
        ls_b.on()         # RSTn HIGH: release reset
        ls_a.on()         # EN HIGH: enable → triggers INITIALIZATION (register reset)
        time.sleep_ms(50) # wait for INITIALIZATION to complete → chip reaches STANDBY
        self._send(0x00, 0x40)
        time.sleep_ms(50)

    def led_on(self, num):
        brightness = led_brightness[num]
        actual_num = led_map[num]
        addr = 0x14 + actual_num
        self._send(addr, brightness)

    def _send(self, addr, data):
        print(f"Sending: addr [{addr}] data [{data}]... ")
        try:
            self.config.i2c.writeto(AL5887, bytes([addr, data]))
            print("done")
        except Exception as e:
            print(f"FAILED: {e}")

    def update(self, delta):

        if self.button_states.get(BUTTON_TYPES["CANCEL"]):
            self.button_states.clear()
            self.minimise()

        if self.button_states.get(BUTTON_TYPES["RIGHT"]):
            for i in range(36):
                self.led_on(i)

        time.sleep_ms(300)

    def draw(self, ctx):
        ctx.save()
        ctx.rgb(0.2, 0, 0).rectangle(-120, -120, 240, 240).fill()
        ctx.rgb(1, 0, 0).move_to(-80, 0).text("Hello world")
        ctx.restore()


__app_export__ = PetalTestApp
