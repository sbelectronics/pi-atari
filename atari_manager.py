"""
    atari_manager

    Used for integrating the atari cartridge with django.
"""

import argparse
import os
import smbus
from threading import Timer
import time
from smbpi.encoder import EncoderThread
from ataricart import AtariCart
import RPi.GPIO as GPIO

ROOT = "root"

CART_FN = 0
CART_NAME = 1
CART_CAT = 2

glo_atari_manager = None

def key_cartridge(x):
    return x[0].lower()

class AtariManager(object):
    def __init__(self, atari, romdir):
        self.atari = atari
        self.romdir = romdir
        self.build_cartridge_db()

        if not self.cartridges:
            raise Exception("No cartridges found")

        default_index = self.pick_default_cartridge()
        self.load_cartridge(self.cartridges[default_index][CART_FN])

    def build_cartridge_db_dir(self, dir, category):
        cartridges = []
        for fn in os.listdir(dir):
            full_fn = os.path.join(dir, fn)
            if os.path.isdir(full_fn) and not fn.startswith("."):
                cartridges = cartridges + self.build_cartridge_db_dir(full_fn, fn)
            if os.path.isfile(full_fn) and (fn.endswith(".bin") or fn.endswith(".a52")):
                cartridges.append((full_fn, fn[:-4], category))

        cartridges = sorted(cartridges, key=key_cartridge)

        #if cartridges:
        #    cartridges = [("", "None", category)] + cartridges

        return cartridges

    def build_cartridge_db(self):
        cartridges = self.build_cartridge_db_dir(self.romdir, ROOT)

        categories = []
        for cart in cartridges:
            if cart[2] not in categories:
                categories.append(cart[2])

        self.cartridges = cartridges
        self.categories = categories

    def pick_default_cartridge(self):
        for i in range(0, len(self.cartridges)):
            if self.cartridges[i][CART_CAT] == "favorites":
                return i
        return 0

    def load_cartridge(self, fn):
        print "Load Cartridge", fn
        self.last_cartridge=fn
        self.atari.interlock_off()
        time.sleep(self.atari.pre_load_delay)
        self.atari.load_cartridge(fn)
        time.sleep(self.atari.post_load_delay)
        self.atari.interlock_on()

    def reset(self):
        self.atari.reset()

    def next_same_category(self, index):
        category = self.cartridges[index][CART_CAT]
        while True:
            index=index+1
            if (index >= len(self.cartridges)):
                index = 0
            if (self.cartridges[index][CART_CAT] == category):
                return index

    def prev_same_category(self, index):
        category = self.cartridges[index][CART_CAT]
        while True:
            index=index-1
            if (index < 0):
                index = len(self.cartridges)-1
            if (self.cartridges[index][CART_CAT] == category):
                return index

    def load_delta(self, delta):
        cart_index = -1
        for i in range (0, len(self.cartridges)):
            if self.cartridges[i][CART_FN] == self.last_cartridge:
                cart_index = i

        if not cart_index:
            raise Exception("could not find current cart")

        while delta != 0:
            if (delta > 0):
                cart_index = self.next_same_category(cart_index)
                delta = delta - 1
            else:
                cart_index = self.prev_same_category(cart_index)
                delta = delta + 1

        self.load_cartridge(self.cartridges[cart_index][CART_FN])

class AtariEncoderThread(EncoderThread):
    def __init__(self, atari_manager, *args, **kwargs):
        self.atari_manager = atari_manager
        self.update_timer = None
        super(AtariEncoderThread, self).__init__(*args, **kwargs)

    def updated(self, handler):
        if self.update_timer is not None:
            self.update_timer.cancel()
            self.update_timer = None
        self.update_timer = Timer(0.25, self.delayed_update)
        self.update_timer.start()

    def delayed_update(self):
        self.update_timer = None
        delta = self.get_delta(0)
        if delta != 0:
            print "Encoder Delta", delta
            self.atari_manager.load_delta(delta)

        if self.get_button_up_event(0):
            print "Encoder Reset"
            self.atari_manager.reset()


def parse_args():
    parser = argparse.ArgumentParser()

    defs = {"encoder": False}

    _help = 'Enable Encoder (default: %s)' % defs['encoder']
    parser.add_argument(
        '-E', '--encoder', dest='encoder', action='store_true',
        default=defs['encoder'],
        help=_help)

    args = parser.parse_args()

    return args

def startup(args):
    global glo_atari_manager

    bus = smbus.SMBus(1)

    atari = AtariCart(bus, 0x20)
    romdir = os.path.join(os.getcwd(), "roms")

    glo_atari_manager = AtariManager(atari, romdir)

    if args.encoder:
        GPIO.setmode(GPIO.BCM)
        glo_encoder_thread = AtariEncoderThread(atari_manager = glo_atari_manager,
                                                encoders = [{"pin_a": 18, "pin_b": 23, "pin_button": 6, "pud": GPIO.PUD_UP, "invert": True}])
        glo_encoder_thread.start()
