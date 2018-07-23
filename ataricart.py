import os
import sys
import threading
import time
from smbpi.dpmem_direct import DualPortMemory
from smbpi.ioexpand import PCF8574

UPPER_ADDR_MASK = ((~0x3F) & 0xFF)

class InterlockManagerThread(threading.Thread):
    """ The 5200 does not like the interlock being powered up before the mainboard power comes online. All I had to
        do is use the lousy spare NAND gates, to tie the interlock_in signal with the desired_interlock. But, I
        didn't, so here we are. Do it in software.
    """

    def __init__(self, ioexpand):
        super(InterlockManagerThread,self).__init__()
        self.daemon = True
        self.desired_interlock = False
        self.actual_interlock = "unknown"
        self.powered_up = False
        self.ioexpand = ioexpand

    def run(self):
        while True:
            self.powered_up = not (self.ioexpand.get_gpio(0) & 0x40)

            should_interlock = self.powered_up and self.desired_interlock

            if (should_interlock != self.actual_interlock):
                if (should_interlock):
                    print "set interlock on", self.desired_interlock, self.powered_up
                    self.ioexpand.or_gpio(0, 0x80)
                else:
                    print "set interlock off", self.desired_interlock, self.powered_up
                    self.ioexpand.not_gpio(0, 0x80)
                self.actual_interlock = should_interlock

            time.sleep(0.001)

class AtariCart():
    def __init__(self, bus, ioexpand_addr):
        self.pre_load_delay=0.2
        self.post_load_delay=0.2
        self.reset_delay=0.4
        self.dpmem = DualPortMemory(n_address_bits=9, enable_reset=False)
        self.ioexpand = PCF8574(bus, ioexpand_addr)
        self.ilock_man = InterlockManagerThread(self.ioexpand)
        self.ilock_man.start()

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
        self.ilock_man.desired_interlock = False
        tries = 0
        while (self.ilock_man.actual_interlock != False):
            time.sleep(0.1)
            tries=tries+1
            if (tries==10):
                print "timeout waiting for interlock to go off"
                return
        #self.ioexpand.not_gpio(0, 0x80)

    def interlock_on(self):
        self.ilock_man.desired_interlock = True
        tries = 0
        while (self.ilock_man.actual_interlock != True):
            time.sleep(0.1)
            tries=tries+1
            if (tries==10):
                print "timeout waiting for interlock to go on"
                return
        #self.ioexpand.or_gpio(0, 0x80)

    def reset(self):
        self.interlock_off()
        time.sleep(self.reset_delay)
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
    cart = AtariCart(bus, 0x20)  # TODO: fix addr

    if (sys.argv[1] == "load"):
        cart.interlock_off()
        time.sleep(cart.pre_load_delay)
        cart.load_cartridge(sys.argv[2])
        cart.verify_cartridge(sys.argv[2])
        time.sleep(cart.post_load_delay)
        cart.interlock_on()

    elif (sys.argv[1] == "verify"):
        cart.verify_cartridge(sys.argv[2])

    elif (sys.argv[1] == "reset"):
        cart.reset()


if __name__ == "__main__":
    main()
