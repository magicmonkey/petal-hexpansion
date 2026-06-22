import asyncio

from app import App
from events.input import Buttons, BUTTON_TYPES
from system.hexpansion.config import HexpansionConfig
import time

AL5887 = 0x30
PORT = 4

class PetalTestApp(App):
    def __init__(self, config=None):
        if config is None:
            config = HexpansionConfig(PORT)
        self.config = config
        self.i2c_devices = []
        self.ls_c_value = None
        self.button_states = Buttons(self)
        self._setup_pins()
        super().__init__()

    def _setup_pins(self):
        ls_a, ls_b, ls_c = self.config.ls_pin[0], self.config.ls_pin[1], self.config.ls_pin[2]
        ls_b.init(ls_b.OUT)
        ls_b.off()        # RSTn LOW: assert hardware reset
        ls_a.init(ls_a.OUT)
        ls_a.off()        # EN LOW: disable during reset
        time.sleep_ms(10)
        ls_b.on()         # RSTn HIGH: release reset
        ls_a.on()         # EN HIGH: enable → triggers INITIALIZATION (register reset)
        time.sleep_ms(50) # wait for INITIALIZATION to complete → chip reaches STANDBY
        ls_c.init(ls_c.IN)

    def _send_range(self, start, finish, data, pause=False):
        for i in range(start, finish+1):
            self._send(i, data)
            if pause:
                time.sleep_ms(50)

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
            self._send(0x00, 0x40)
            time.sleep_ms(10)
            self._send_range(0x08, 0x13, 0x40)
            self._send_range(0x14, 0x37, 0xff, True)
            time.sleep_ms(300)

    def draw(self, ctx):
        ctx.save()
        ctx.rgb(0.2, 0, 0).rectangle(-120, -120, 240, 240).fill()
        ctx.rgb(1, 0, 0).move_to(-80, 0).text("Hello world")
        ctx.restore()


__app_export__ = PetalTestApp
