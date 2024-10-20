import sys

import m5
from m5.defines import buildEnv
from m5.objects import *
from m5.util import addToPath

addToPath("../../")
from common.Caches import *
from common.cpu2000 import *
from common.FileSystemConfig import config_filesystem


class gate_control:
    def __init__(self, system):
        self.system = system

    def toogle_gate_control(self, freq, voltage):
        self.system.cpu_clk_domain.clock = freq
        self.system.clk_domain.clock = freq
        self.system.cpu_voltage_domain.voltage = voltage
        self.system.cpu_clk_domain.voltage_domain.voltage = voltage
        return self.system


class L1Cache(Cache):
    """Simple L1 Cache with default values"""

    assoc = 2
    tag_latency = 2
    data_latency = 2
    response_latency = 2
    mshrs = 4
    tgts_per_mshr = 20

    def __init__(self, options=None):
        super().__init__()
        pass

    def connectBus(self, bus):
        """Connect this cache to a memory-side bus"""
        self.mem_side = bus.cpu_side_ports

    def connectCPU(self, cpu):
        """Connect this cache's port to a CPU-side port
        This must be defined in a subclass"""
        raise NotImplementedError


class L1ICache(L1Cache):
    """Simple L1 instruction cache with default values"""

    # Set the default size
    size = "64kB"

    def __init__(self, opts=None):
        super().__init__(opts)
        if not opts or not opts.l1i_size:
            return
        self.size = opts.l1i_size

    def connectCPU(self, cpu):
        """Connect this cache's port to a CPU icache port"""
        self.cpu_side = cpu.icache_port


class L1DCache(L1Cache):
    """Simple L1 data cache with default values"""

    # Set the default size
    size = "256kB"

    def __init__(self, opts=None):
        super().__init__(opts)
        if not opts or not opts.l1d_size:
            return
        self.size = opts.l1d_size

    def connectCPU(self, cpu):
        """Connect this cache's port to a CPU dcache port"""
        self.cpu_side = cpu.dcache_port


class L2Cache(Cache):
    """Simple L2 Cache with default values"""

    size = "1MB"
    assoc = 8
    tag_latency = 20
    data_latency = 20
    response_latency = 20
    mshrs = 20
    tgts_per_mshr = 12

    def __init__(self, opts=None):
        super().__init__()
        if not opts or not opts.l2_size:
            return
        self.size = opts.l2_size

    def connectCPUSideBus(self, bus):
        self.cpu_side = bus.mem_side_ports

    def connectMemSideBus(self, bus):
        self.mem_side = bus.cpu_side_ports


system = System()
system.clk_domain = SrcClockDomain()
system.cpu_voltage_domain = VoltageDomain()
system.cpu_clk_domain = SrcClockDomain()
system.clk_domain.voltage_domain = VoltageDomain()
system.cpu_clk_domain.voltage_domain = VoltageDomain()
system.mem_mode = "timing"
system.mem_ranges = [AddrRange("8192MB")]
system.cpu = TimingSimpleCPU()
system.membus = SystemXBar()

system.mem_ctrl = MemCtrl()
system.mem_ctrl.dram = DDR3_1600_8x8()
system.mem_ctrl.dram.range = system.mem_ranges[0]
system.mem_ctrl.port = system.membus.mem_side_ports

system.cpu.icache = L1ICache()
system.cpu.dcache = L1DCache()

system.cpu.icache.cpu_side = system.cpu.icache_port
system.cpu.dcache.cpu_side = system.cpu.dcache_port

system.cpu.icache.mem_side = system.membus.cpu_side_ports
system.cpu.dcache.mem_side = system.membus.cpu_side_ports

system.cpu.createInterruptController()
system.cpu.interrupts[0].pio = system.membus.mem_side_ports
system.cpu.interrupts[0].int_requestor = system.membus.cpu_side_ports
system.cpu.interrupts[0].int_responder = system.membus.mem_side_ports
system.system_port = system.membus.cpu_side_ports

binary = sys.argv[sys.argv.index("-c") + 1]
process = Process()
process.cmd = [binary]
system.cpu.workload = process
system.cpu.createThreads()
system.workload = SEWorkload.init_compatible(binary)

dvfs = gate_control(system)


system = dvfs.toogle_gate_control("4.0GHz", "1.0V")
root = Root(full_system=False, system=system)
m5.instantiate()

print(f"Beginning simulation!")
exit_event = m5.simulate()
print(f"Exiting @ tick {m5.curTick()} because {exit_event.getCause()}")
