import sys

import m5
from m5.defines import buildEnv
from m5.objects import *
from m5.util import addToPath

# Add the gem5 path to access common components
addToPath("../../")

# Import common components for caches and file system configurations
from common.Caches import *
from common.cpu2000 import *
from common.FileSystemConfig import config_filesystem


# Class to control the clock and voltage for dynamic voltage and frequency scaling (DVFS)
class gate_control:
    def __init__(self, system):
        self.system = system

    def toogle_gate_control(self, freq, voltage):
        """
        Toggle the system's frequency and voltage.
        """
        self.system.cpu_clk_domain.clock = freq
        self.system.clk_domain.clock = freq
        self.system.cpu_voltage_domain.voltage = voltage
        self.system.cpu_clk_domain.voltage_domain.voltage = voltage
        return self.system


# Base class for L1 cache configuration
class L1Cache(Cache):
    """Simple L1 Cache with default values"""

    # Default cache properties
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
        """
        Connect this cache's port to a CPU-side port.
        To be implemented in subclass.
        """
        raise NotImplementedError


# L1 Instruction Cache class
class L1ICache(L1Cache):
    """Simple L1 instruction cache with default values"""

    # Default size of instruction cache
    size = "64kB"

    def __init__(self, opts=None):
        super().__init__(opts)
        if opts and opts.l1i_size:
            self.size = opts.l1i_size

    def connectCPU(self, cpu):
        """Connect this cache's port to a CPU icache port"""
        self.cpu_side = cpu.icache_port


# L1 Data Cache class
class L1DCache(L1Cache):
    """Simple L1 data cache with default values"""

    # Default size of data cache
    size = "256kB"

    def __init__(self, opts=None):
        super().__init__(opts)
        if opts and opts.l1d_size:
            self.size = opts.l1d_size

    def connectCPU(self, cpu):
        """Connect this cache's port to a CPU dcache port"""
        self.cpu_side = cpu.dcache_port


# L2 Cache class
class L2Cache(Cache):
    """Simple L2 Cache with default values"""

    # Default cache properties
    size = "1MB"
    assoc = 8
    tag_latency = 20
    data_latency = 20
    response_latency = 20
    mshrs = 20
    tgts_per_mshr = 12

    def __init__(self, opts=None):
        super().__init__(opts)
        if opts and opts.l2_size:
            self.size = opts.l2_size

    def connectCPUSideBus(self, bus):
        self.cpu_side = bus.mem_side_ports

    def connectMemSideBus(self, bus):
        self.mem_side = bus.cpu_side_ports


# System configuration
system = System()

# Define clock and voltage domains
system.clk_domain = SrcClockDomain()
system.cpu_voltage_domain = VoltageDomain()
system.cpu_clk_domain = SrcClockDomain()

# Set the voltage domain for the clock domains
system.clk_domain.voltage_domain = VoltageDomain()
system.cpu_clk_domain.voltage_domain = VoltageDomain()

# Set memory mode and ranges
system.mem_mode = "timing"
system.mem_ranges = [AddrRange("8192MB")]

# Define CPU and memory bus
system.cpu = TimingSimpleCPU()
system.membus = SystemXBar()

# Memory controller configuration (DDR3)
system.mem_ctrl = MemCtrl()
system.mem_ctrl.dram = DDR3_1600_8x8()
system.mem_ctrl.dram.range = system.mem_ranges[0]
system.mem_ctrl.port = system.membus.mem_side_ports

# Connect instruction and data caches to the CPU and bus
system.cpu.icache = L1ICache()
system.cpu.dcache = L1DCache()

system.cpu.icache.cpu_side = system.cpu.icache_port
system.cpu.dcache.cpu_side = system.cpu.dcache_port

system.cpu.icache.mem_side = system.membus.cpu_side_ports
system.cpu.dcache.mem_side = system.membus.cpu_side_ports

# Set up interrupt controller for the CPU
system.cpu.createInterruptController()
system.cpu.interrupts[0].pio = system.membus.mem_side_ports
system.cpu.interrupts[0].int_requestor = system.membus.cpu_side_ports
system.cpu.interrupts[0].int_responder = system.membus.mem_side_ports

# Set the system port to the memory bus
system.system_port = system.membus.cpu_side_ports

# Set the binary file to be executed as part of the workload
binary = sys.argv[sys.argv.index("-c") + 1]
process = Process()
process.cmd = [binary]
system.cpu.workload = process
system.cpu.createThreads()
system.workload = SEWorkload.init_compatible(binary)

# Apply Dynamic Voltage and Frequency Scaling (DVFS)
dvfs = gate_control(system)
system = dvfs.toogle_gate_control("4.0GHz", "1.0V")

# Instantiate the root system object and start simulation
root = Root(full_system=False, system=system)
m5.instantiate()

# Begin the simulation
print(f"Beginning simulation!")
exit_event = m5.simulate()

# Print the simulation exit reason
print(f"Exiting @ tick {m5.curTick()} because {exit_event.getCause()}")
