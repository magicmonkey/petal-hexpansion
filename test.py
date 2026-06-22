import asyncio

from app import App
from events.input import Buttons, BUTTON_TYPES
from system.hexpansion.config import HexpansionConfig
from system.eventbus import eventbus
from system.hexpansion.events import HexpansionRemovalEvent, HexpansionInsertionEvent
from system.hexpansion.app import HexpansionManagerApp
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

petals = [
    False,
    False,
    False,
    False,
    False,
    False,
]

class PetalTestApp(App):
    def __init__(self):
        eventbus.on(
            HexpansionInsertionEvent,
            self.handle_hexpansion_insertion,
            self)
        eventbus.on(
            HexpansionRemovalEvent,
            self.handle_hexpansion_removal,
            self)
        self.button_states = Buttons(self)
        self.scan_i2c()
        super().__init__()

    def scan_i2c(self):
        for i, pin in enumerate(HexpansionManagerApp.hexpansion_pins):
            if not pin.value():
                petals[i] = HexpansionConfig(i+1)
                self._setup_pins(petals[i])
            else:
                petals[i] = False

    def handle_hexpansion_insertion(self, event):
        self.scan_i2c()

    def handle_hexpansion_removal(self, event):
        self.scan_i2c()

    def _setup_pins(self, port):
        ls_a, ls_b, ls_c = port.ls_pin[0], port.ls_pin[1], port.ls_pin[2]
        ls_c.init(ls_c.IN)
        ls_b.init(ls_b.OUT)
        ls_b.off()        # RSTn LOW: assert hardware reset
        ls_a.init(ls_a.OUT)
        ls_a.off()        # EN LOW: disable during reset
        time.sleep_ms(10)
        ls_b.on()         # RSTn HIGH: release reset
        ls_a.on()         # EN HIGH: enable → triggers INITIALIZATION (register reset)
        time.sleep_ms(50) # wait for INITIALIZATION to complete → chip reaches STANDBY
        self._send(port, 0x00, 0x40)
        time.sleep_ms(50)

    def led(self, port, num, brightness):
        brightness = int((brightness / 0xff) * led_brightness[num])
        actual_num = led_map[num]
        addr = 0x14 + actual_num
        self._send(port, addr, brightness)

    def led_on(self, port, num):
        self.led(port, num, 0xff)

    def led_off(self, port, num):
        self.led(port, num, 0)

    def _send(self, port, addr, data):
        try:
            port.i2c.writeto(AL5887, bytes([addr, data]))
        except Exception as e:
            print(f"Sending failed: addr [{addr}] data [{data}]")
            print(e)

    def update(self, delta):

        if self.button_states.get(BUTTON_TYPES["CANCEL"]):
            self.button_states.clear()
            self.minimise()

        if self.button_states.get(BUTTON_TYPES["RIGHT"]):
            for i in range(36):
                for petal in petals:
                    if petal:
                        self.led_on(petal, i)

        if self.button_states.get(BUTTON_TYPES["LEFT"]):
            for i in range(36):
                for petal in petals:
                    if petal:
                        self.led_off(petal, i)

        time.sleep_ms(300)

    def draw(self, ctx):
        ctx.save()
        ctx.rgb(0.2, 0, 0).rectangle(-120, -120, 240, 240).fill()
        ctx.rgb(1, 0, 0).move_to(-80, 0).text("Hello world")
        ctx.restore()


__app_export__ = PetalTestApp
