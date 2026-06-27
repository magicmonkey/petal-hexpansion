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

OUTER  = 4
MIDDLE = 64
INNER  = 2

led_brightness = [
    OUTER, OUTER, OUTER, OUTER, OUTER, OUTER, OUTER, OUTER, OUTER, OUTER, OUTER, OUTER, OUTER, OUTER, OUTER, OUTER, OUTER, OUTER, OUTER, 
    MIDDLE, MIDDLE, MIDDLE, MIDDLE, MIDDLE, MIDDLE, MIDDLE, MIDDLE, MIDDLE, MIDDLE, MIDDLE, MIDDLE, 
    INNER, INNER, INNER, INNER, INNER, 
]


class petals:

    def __init__(self):
        self.petals = [
            False,
            False,
            False,
            False,
            False,
            False,
        ]

    def set_petal(self, petal, num):
        self.petals[num] = petal
        self._setup_pins(num)

    def remove_petal(self, num):
        self.petals[num] = False

    def _setup_pins(self, port):
        gpio = self.petals[port]
        ls_a, ls_b, ls_c = gpio.ls_pin[0], gpio.ls_pin[1], gpio.ls_pin[2]
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

        self.brightness(5)

    # Brightness setting, 0-64.  Uses the 0x66 register on the AL5887
    def brightness(self, brt):
        b = 0
        if brt > 63:
            b = 31
        elif brt > 31:
            b = brt - 32
        else:
            b = brt + 32

        for petal in range(6):
            self._send(petal, 0x66, b)

    def all_led_off(self):
        self.all_led_outer_off()
        self.all_led_middle_off()
        self.all_led_inner_off()

    def all_led_outer_on(self):
        for p in range(6):
            self.led_outer_on(p)

    def all_led_outer_off(self):
        for p in range(6):
            self.led_outer_off(p)

    def all_led_middle_on(self):
        for p in range(6):
            self.led_middle_on(p)

    def all_led_middle_off(self):
        for p in range(6):
            self.led_middle_off(p)

    def all_led_inner_on(self):
        for p in range(6):
            self.led_inner_on(p)

    def all_led_inner_off(self):
        for p in range(6):
            self.led_inner_off(p)

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
        addr = 0x14 + actual_num  # From the AL5887 datasheet, the individual LED control starts at 0x14
        self._send(port, addr, brightness)

    def _send(self, port, addr, data):
        if not self.petals[port]:
            return
        try:
            self.petals[port].i2c.writeto(AL5887, bytes([addr, data]))
        except Exception as e:
            print(f"Sending failed: addr [{addr}] data [{data}]")
            print(e)

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
        self.led_outer_on(self.petals[0])
        time.sleep_ms(200)
        self.led_outer_on(self.petals[1])
        time.sleep_ms(200)
        self.led_outer_on(self.petals[2])
        time.sleep_ms(200)
        self.led_outer_on(self.petals[3])
        time.sleep_ms(200)
        self.led_outer_on(self.petals[4])
        time.sleep_ms(200)
        self.led_outer_on(self.petals[5])
        time.sleep_ms(200)
        self.led_middle_on(self.petals[0])
        time.sleep_ms(200)
        self.led_middle_on(self.petals[1])
        time.sleep_ms(200)
        self.led_middle_on(self.petals[2])
        time.sleep_ms(200)
        self.led_middle_on(self.petals[3])
        time.sleep_ms(200)
        self.led_middle_on(self.petals[4])
        time.sleep_ms(200)
        self.led_middle_on(self.petals[5])
        time.sleep_ms(200)
        self.led_inner_on(self.petals[0])
        time.sleep_ms(200)
        self.led_inner_on(self.petals[1])
        time.sleep_ms(200)
        self.led_inner_on(self.petals[2])
        time.sleep_ms(200)
        self.led_inner_on(self.petals[3])
        time.sleep_ms(200)
        self.led_inner_on(self.petals[4])
        time.sleep_ms(200)
        self.led_inner_on(self.petals[5])
        time.sleep_ms(200)

    def anim3(self):
        for petal in self.petals:
            if not petal:
                continue
            for i in range(19-1, 0-1, -1):
                self.led_on(petal, i)
                time.sleep_ms(10)
        for petal in self.petals:
            if not petal:
                continue
            for i in range(19+12-1, 19-1, -1):
                self.led_on(petal, i)
                time.sleep_ms(10)
        for petal in self.petals:
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
        petal = self.petals[0]
        for count in range(5):
            for b in range(16):
                for i in range(19):
                    self.led(petal, i, b, False)
                time.sleep_ms(50)
            for b in range(15, -1, -1):
                for i in range(19):
                    self.led(petal, i, b, False)
                time.sleep_ms(50)
