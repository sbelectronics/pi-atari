"""
    atari_manager

    Used for integrating the atari cartridge with django.
"""

import argparse
import os
import smbus
from ataricart import AtariCart

glo_atari = None
glo_romdir = None

def key_cartridge(x):
    return x[0].lower()

def list_cartridges():
    filenames = []
    for fn in os.listdir(glo_romdir):
        full_fn = os.path.join(glo_romdir, fn)
        if os.path.isfile(full_fn) and fn.endswith(".bin"):
            filenames.append( (full_fn, fn[:-4]) )

    filenames = sorted(filenames, key=key_cartridge)

    filenames = [ ("", "None") ] + filenames

    return filenames

def parse_args():
    parser = argparse.ArgumentParser()
    args = parser.parse_args()

    return args

def startup(args):
    global glo_atari, glo_romdir
   
    bus = smbus.SMBus(1)

    glo_atari = AtariCart(bus, 0x20)

    glo_romdir = os.path.join(os.getcwd(), "roms")
