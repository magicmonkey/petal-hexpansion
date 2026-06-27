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
from animations import anim1

MENU_ITEMS = [
    ("Anim 1",   "anim1"),
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
        if item == "Anim 1":
            anim1.anim(self.petals)
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
