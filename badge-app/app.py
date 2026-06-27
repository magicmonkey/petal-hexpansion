import sys
import os
import asyncio

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

def _discover_animations():
    anim_dir = sys.path[0] + '/animations'
    discovered = []
    try:
        for filename in sorted(os.listdir(anim_dir)):
            if filename.endswith('.py') and filename != '__init__.py':
                module_name = filename[:-3]
                top = __import__('animations.' + module_name)
                module = getattr(top, module_name)
                name = getattr(module, 'NAME', module_name)
                discovered.append((name, module))
    except OSError:
        pass
    return discovered

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
        self.animations = _discover_animations()
        self.current_anim_task = None
        self.menu = Menu(
            self,
            [name for name, _ in self.animations],
            select_handler=self.select_handler,
            back_handler=self.back_handler,
        )
        self.petals = petals()
        self.scan_for_petals()
        super().__init__()

    def select_handler(self, item, position):
        if self.current_anim_task is not None:
            self.current_anim_task.cancel()
        _, module = self.animations[position]
        self.current_anim_task = asyncio.create_task(module.anim(self.petals))

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
