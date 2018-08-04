"""
    atari_manager

    Used for integrating the atari cartridge with django.
"""

import argparse
import os
import smbus
from ataricart import AtariCart

ROOT = "root"

glo_atari = None
glo_romdir = None

def key_cartridge(x):
    return x[0].lower()

def list_cartridges(dir=None, category=ROOT):
    if not dir:
        dir = glo_romdir

    filenames = []
    for fn in os.listdir(dir):
        full_fn = os.path.join(dir, fn)
        if os.path.isdir(full_fn) and not fn.startswith("."):
            filenames = filenames + list_cartridges(full_fn, fn)
        if os.path.isfile(full_fn) and (fn.endswith(".bin") or fn.endswith(".a52")):
            filenames.append( (full_fn, fn[:-4], category) )

    filenames = sorted(filenames, key=key_cartridge)

    if filenames:
        filenames = [ ("", "None", category) ] + filenames

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
