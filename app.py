import asyncio
import sys

from app import App
from app_components import Menu, clear_background
from events.input import Buttons, BUTTON_TYPES
from system.hexpansion.config import HexpansionConfig
from system.eventbus import eventbus
from system.hexpansion.events import HexpansionRemovalEvent, HexpansionInsertionEvent
from system.hexpansion.app import HexpansionManagerApp
import time

sys.path.insert(0, '/apps/petal')
from led import petals

MENU_ITEMS = [
    ("Ripple",   "anim1"),
    ("Spiral",   "anim2"),
    ("Fill",     "anim3"),
    ("Pulse",    "anim4"),
    ("Fade In",  "anim5"),
    ("Shimmer",  "anim6"),
    ("Lights Off", "all_led_off"),
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
        self.menu = Menu(
            self,
            [name for name, _ in MENU_ITEMS],
            select_handler=self.select_handler,
            back_handler=self.back_handler,
        )
        self.petals = petals()
        self.scan_for_petals()
        super().__init__()

    def select_handler(self, item, position):
        for name, method in MENU_ITEMS:
            if name == item:
                getattr(self.petals, method)()
                return

    def back_handler(self):
        self.minimise()

    def scan_for_petals(self):
        for i, pin in enumerate(HexpansionManagerApp.hexpansion_pins):
            if not pin.value():
                self.petals.set_petal(HexpansionConfig(i+1), i)
            else:
                self.petals.remove_petal(i)

    def handle_hexpansion_insertion(self, event):
        self.scan_for_petals()

    def handle_hexpansion_removal(self, event):
        self.scan_for_petals()

    def update(self, delta):
        self.menu.update(delta)

    def draw(self, ctx):
        clear_background(ctx)
        self.menu.draw(ctx)


__app_export__ = PetalTestApp
