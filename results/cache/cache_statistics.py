import pandas as pd
import matplotlib.pyplot as plt

# Read the data from the file
file_path = 'results/cache/1GHZ_1V_Double_L1Cache.txt'

# Function to parse the file and extract relevant statistics
def parse_file(file_path):
    data = {}
    with open(file_path, 'r') as file:
        for line in file:
            if '::' in line:
                key, value = line.split('::')
                key = key.strip()
                value = value.split('#')[0].strip()  # Remove comments
                data[key] = float(value) if value.replace('.', '', 1).isdigit() else value
    return data

# Parse the file
data = parse_file(file_path)

# Prepare data for plotting
labels = [
    'Read Hits', 
    'Write Hits', 
    'Read Misses', 
    'Write Misses', 
    'Demand Accesses', 
    'Overall Accesses'
]
values = [
    data['system.cpu.dcache.ReadReq.hits'],         # Read Hits
    data['system.cpu.dcache.WriteReq.hits'],        # Write Hits
    data['system.cpu.dcache.ReadReq.misses'],       # Read Misses
    data['system.cpu.dcache.WriteReq.misses'],      # Write Misses
    data['system.cpu.dcache.demandAccesses'],       # Demand Accesses
    data['system.cpu.dcache.overallAccesses'],      # Overall Accesses
]

# Create the bar plot
plt.figure(figsize=(10, 6))
plt.bar(labels, values, color='yellow')
plt.title('4GHZ_1V_Quadruple_Cache')
plt.xlabel('Metrics')
plt.ylabel('Counts')
plt.xticks(rotation=45)
plt.grid(axis='y')

# Show the plot
plt.tight_layout()
plt.show()
