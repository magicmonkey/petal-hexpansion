import asyncio

# from apps.petal.test import __app_export__

from app import App
from events.input import Buttons, BUTTON_TYPES
from system.hexpansion.config import HexpansionConfig
from system.eventbus import eventbus
from system.hexpansion.events import HexpansionRemovalEvent, HexpansionInsertionEvent
from system.hexpansion.app import HexpansionManagerApp
import time

AL5887 = 0x30

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

OUTER  = 8
MIDDLE = 255
INNER  = 8

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

    def brightness(self, brt):
        b = 0
        if brt > 63:
            b = 31
        elif brt > 31:
            b = brt - 32
        else:
            b = brt + 32

        for petal in petals:
            if petal:
                self._send(petal, 0x66, b)

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

    def all_led_off(self):
        self.all_led_outer_off()
        self.all_led_middle_off()
        self.all_led_inner_off()

    def all_led_outer_on(self):
        for petal in petals:
            if petal:
                self.led_outer_on(petal)

    def all_led_outer_off(self):
        for petal in petals:
            if petal:
                self.led_outer_off(petal)

    def all_led_middle_on(self):
        for petal in petals:
            if petal:
                self.led_middle_on(petal)

    def all_led_middle_off(self):
        for petal in petals:
            if petal:
                self.led_middle_off(petal)

    def all_led_inner_on(self):
        for petal in petals:
            if petal:
                self.led_inner_on(petal)

    def all_led_inner_off(self):
        for petal in petals:
            if petal:
                self.led_inner_off(petal)

    def led_outer_on(self, port):
        for i in range(19):
            self.led_on(port, i)

    def led_outer_off(self, port):
        for i in range(19):
            self.led_off(port, i)

    def led_middle_on(self, port):
        for i in range(19, 19+12):
            self.led_on(port, i)

    def led_middle_off(self, port):
        for i in range(19, 19+12):
            self.led_off(port, i)

    def led_inner_on(self, port):
        for i in range(19+12, 19+12+5):
            self.led_on(port, i)

    def led_inner_off(self, port):
        for i in range(19+12, 19+12+5):
            self.led_off(port, i)

    def led_on(self, port, num):
        self.led(port, num, 0xff)

    def led_off(self, port, num):
        self.led(port, num, 0)

    def led(self, port, num, brightness, modulation=True):
        if modulation:
            brightness = int((brightness / 0xff) * led_brightness[num])
        actual_num = led_map[num]
        addr = 0x14 + actual_num
        self._send(port, addr, brightness)

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
            self.anim2()
            self.anim1()
            self.anim3()
            self.anim1()
            self.anim2()
            self.anim4()
            self.anim4()
            self.anim4()
            self.anim1()

        if self.button_states.get(BUTTON_TYPES["UP"]):
            self.anim2()

        if self.button_states.get(BUTTON_TYPES["DOWN"]):
            self.anim3()

        if self.button_states.get(BUTTON_TYPES["LEFT"]):
            self.all_led_off()

        time.sleep_ms(300)

    def anim1(self):
        self.all_led_outer_on()
        time.sleep_ms(250)
        self.all_led_outer_off()
        self.all_led_middle_on()
        time.sleep_ms(250)
        self.all_led_middle_off()
        self.all_led_inner_on()
        time.sleep_ms(250)
        self.all_led_inner_off()

    def anim2(self):
        self.led_outer_on(petals[0])
        time.sleep_ms(200)
        self.led_outer_on(petals[1])
        time.sleep_ms(200)
        self.led_outer_on(petals[2])
        time.sleep_ms(200)
        self.led_outer_on(petals[3])
        time.sleep_ms(200)
        self.led_outer_on(petals[4])
        time.sleep_ms(200)
        self.led_outer_on(petals[5])
        time.sleep_ms(200)
        self.led_middle_on(petals[0])
        time.sleep_ms(200)
        self.led_middle_on(petals[1])
        time.sleep_ms(200)
        self.led_middle_on(petals[2])
        time.sleep_ms(200)
        self.led_middle_on(petals[3])
        time.sleep_ms(200)
        self.led_middle_on(petals[4])
        time.sleep_ms(200)
        self.led_middle_on(petals[5])
        time.sleep_ms(200)
        self.led_inner_on(petals[0])
        time.sleep_ms(200)
        self.led_inner_on(petals[1])
        time.sleep_ms(200)
        self.led_inner_on(petals[2])
        time.sleep_ms(200)
        self.led_inner_on(petals[3])
        time.sleep_ms(200)
        self.led_inner_on(petals[4])
        time.sleep_ms(200)
        self.led_inner_on(petals[5])
        time.sleep_ms(200)

    def anim3(self):
        for petal in petals:
            if not petal:
                continue
            for i in range(19-1, 0-1, -1):
                self.led_on(petal, i)
                time.sleep_ms(10)
        for petal in petals:
            if not petal:
                continue
            for i in range(19+12-1, 19-1, -1):
                self.led_on(petal, i)
                time.sleep_ms(10)
        for petal in petals:
            if not petal:
                continue
            for i in range(19+12+5-1, 19+12-1, -1):
                self.led_on(petal, i)
                time.sleep_ms(10)

    def anim4(self):
        self.all_led_outer_on()
        self.all_led_middle_on()
        self.all_led_inner_on()
        time.sleep_ms(300)
        self.all_led_inner_off()
        time.sleep_ms(300)
        self.all_led_inner_on()
        self.all_led_middle_off()
        time.sleep_ms(300)
        self.all_led_middle_on()
        self.all_led_outer_off()
        time.sleep_ms(300)
        self.all_led_outer_on()

    def anim5(self):
        self.brightness(0)
        self.all_led_outer_on()
        self.all_led_middle_on()
        self.all_led_inner_on()

        for i in range(0, 64):
            self.brightness(i)
            time.sleep_ms(30)

    def anim6(self):
        petal = petals[0]
        for count in range(5):
            for b in range(16):
                for i in range(19):
                    self.led(petal, i, b, False)
                time.sleep_ms(50)
            for b in range(15, -1, -1):
                for i in range(19):
                    self.led(petal, i, b, False)
                time.sleep_ms(50)

    def draw(self, ctx):
        ctx.save()
        ctx.rgb(0.2, 0, 0).rectangle(-120, -120, 240, 240).fill()
        ctx.rgb(1, 0, 0).move_to(-80, 0).text("Hello world")
        ctx.restore()


__app_export__ = PetalTestApp
