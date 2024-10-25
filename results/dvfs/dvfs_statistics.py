import matplotlib.pyplot as plt

# Define a function to parse the file and extract relevant data
def parse_simulation_file(file_path):
    data = {
        "simSeconds": None,
        "simTicks": None,
        "finalTick": None,
        "hostSeconds": None,
        "hostMemory": None,
        "dcacheMissRate": None,
        "icacheMissRate": None,
        "dramReadBandwidth": None,
        "cpuCycles": None,
        "cpuIPC": None,
        "cpuCPI": None
    }
    
    with open(file_path, 'r') as file:
        for line in file:
            if "simSeconds" in line:
                data["simSeconds"] = float(line.split()[1])
            elif "simTicks" in line:
                data["simTicks"] = int(line.split()[1])
            elif "finalTick" in line:
                data["finalTick"] = int(line.split()[1])
            elif "hostSeconds" in line:
                data["hostSeconds"] = float(line.split()[1])
            elif "hostMemory" in line:
                data["hostMemory"] = int(line.split()[1])
            elif "system.cpu.dcache.demandMissRate::total" in line:
                data["dcacheMissRate"] = float(line.split()[1])
            elif "system.cpu.icache.demandMissRate::total" in line:
                data["icacheMissRate"] = float(line.split()[1])
            elif "system.mem_ctrl.dram.bwRead::total" in line:
                data["dramReadBandwidth"] = float(line.split()[1])
            elif "system.cpu.numCycles" in line:
                data["cpuCycles"] = int(line.split()[1])
            elif "system.cpu.ipc" in line:
                data["cpuIPC"] = float(line.split()[1])
            elif "system.cpu.cpi" in line:
                data["cpuCPI"] = float(line.split()[1])
    
    return data

# Plot 1: Cache Miss Rate (Data Cache and Instruction Cache)
def plot_cache_miss_rate(data):
    labels = ['Data Cache Miss Rate', 'Instruction Cache Miss Rate']
    miss_rates = [data['dcacheMissRate'], data['icacheMissRate']]

    plt.bar(labels, miss_rates, color=['blue', 'green'])
    plt.title('Cache Miss Rate')
    plt.ylabel('Miss Rate')
    plt.show()

# Plot 2: DRAM Read Bandwidth
def plot_dram_read_bandwidth(data):
    plt.bar(['DRAM Read Bandwidth'], [data['dramReadBandwidth'] / (1024 * 1024)], color='purple')  # Convert to MB/s
    plt.title('DRAM Read Bandwidth')
    plt.ylabel('Bandwidth (MB/s)')
    plt.show()

# Plot 3: CPU IPC and CPI
def plot_cpu_ipc_cpi(data):
    labels = ['IPC', 'CPI']
    values = [data['cpuIPC'], data['cpuCPI']]

    plt.bar(labels, values, color=['orange', 'red'])
    plt.title('CPU IPC and CPI')
    plt.show()

# Main execution
file_path = 'results/dvfs/1GHZ_1V_Small_Cache.txt'  # Update this path to where your file is stored
data = parse_simulation_file(file_path)

# Check if data was parsed successfully
if all(data.values()):
    # Plotting all the graphs
    plot_cache_miss_rate(data)
    plot_dram_read_bandwidth(data)
    plot_cpu_ipc_cpi(data)
else:
    print("Some data could not be parsed. Please check the file format.")
