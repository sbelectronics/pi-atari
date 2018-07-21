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

def list_cartridges():
    filenames = []
    for fn in os.listdir(glo_romdir):
        if os.path.isfile(fn) and fn.endswith(".bin"):
            filenames.append(fn)

    filenames = sorted(filenames, key=str.lower)

    result=[]
    for filename in filenames:
        result.append( (filename, filename) )

    return result

def parse_args():
    parser = argparse.ArgumentParser()
    args = parser.parse_args()

    return args

def startup(args):
    global glo_atari
   
    bus = smbus.SMBus(1)

    glo_atari = AtariCart(bus, 0x20)

    glo_atari = atari
    glo_romdir = "roms"
