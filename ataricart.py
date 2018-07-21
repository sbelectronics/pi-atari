import os
import sys
import time
from smbpi.dpmem_direct import DualPortMemory
from smbpi.ioexpand import PCF8574

UPPER_ADDR_MASK = ((~0x3F) & 0xFF)

class AtariCart():
    def __init__(self, bus, ioexpand_addr):
        self.dpmem = DualPortMemory(n_address_bits=9, enable_reset=False)
        self.ioexpand = PCF8574(bus, ioexpand_addr)

    def write_block(self, addr, data):
        while (len(data) > 0):
            upper_addr = addr >> 9
            lower_addr = addr & 0x1FF
            self.ioexpand.set_gpio(0, (self.ioexpand.gpio_bits & UPPER_ADDR_MASK) | upper_addr)
            self.dpmem.write_block(lower_addr, data, min(512, len(data)))
            data = data[512:]
            addr += 512

    def verify_block(self, addr, data):
        while (len(data) > 0):
            upper_addr = addr >> 9
            lower_addr = addr & 0x1FF
            self.ioexpand.set_gpio(0, (self.ioexpand.gpio_bits & UPPER_ADDR_MASK) | upper_addr)
            read_data = self.dpmem.read_block(lower_addr, min(512, len(data)))
 
            for i in range(0, min(512, len(data))):
                if data[i] != read_data[i]:
                    print "verify error addr=%06X, file=%02X, cart=%02X" % (addr + i, ord(data[i]), ord(read_data[i]))

            data = data[512:]
            addr += 512

    def interlock_off(self):
        self.ioexpand.not_gpio(0, 0x80)

    def interlock_on(self):
        self.ioexpand.or_gpio(0, 0x80)

    def reset(self):
        self.interlock_off()
        time.sleep(0.1)
        self.interlock_on()

    def load_cartridge(self, fn):
        data = open(fn, "rb").read()
        if len(data)==16384:
            self.write_block(0, data[:8192])
            self.write_block(8192, data[:8192])
            self.write_block(16384, data[8192:])
            self.write_block(24576, data[8192:])
        else:
            self.write_block(0, data)

    def verify_cartridge(self, fn):
        data = open(fn, "rb").read()
        if len(data)==16384:
            self.verify_block(0, data[:8192])
            self.verify_block(8192, data[:8192])
            self.verify_block(16384, data[8192:])
            self.verify_block(24576, data[8192:])
        else:
            self.verify_block(0, data)

def main():
    import smbus

    bus = smbus.SMBus(1)
    cart = AtariCart(bus, 0x20) # TODO: fix addr
    cart.interlock_off()
    cart.load_cartridge(sys.argv[1])
    cart.verify_cartridge(sys.argv[1])
    cart.interlock_on()

if __name__ == "__main__":
    main()
