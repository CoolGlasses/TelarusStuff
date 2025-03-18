import re
import numpy as np

# Initialize lists to store load times
opportunity_times = []
case_times = []
order_times = []

input_file = "locustUI.log"
output_file = "plttest_lines.log"
keyword = "plttest"
def filter_log(input_file, output_file, keyword):
    with open(input_file, "r", encoding="utf-8") as infile, open(output_file, "w", encoding="utf-8") as outfile:
        for line in infile:
            if keyword in line:
                outfile.write(line)


filter_log(input_file,output_file,keyword)
with open('plttest_lines.log', 'r') as file:
    for line in file:
        # Extract the load time using regex
        match = re.search(r'Time to load (Opportunity|Case|Order): (\d+\.\d+) seconds', line)
        if match:
            component = match.group(1)
            load_time = float(match.group(2))
            if component == 'Opportunity':
                opportunity_times.append(load_time)
            elif component == 'Case':
                case_times.append(load_time)
            elif component == 'Order':
                order_times.append(load_time)

# Function to calculate percentile safely
def calculate_percentile(data, percentile):
    if data:  # Check if the list is not empty
        return np.percentile(data, percentile)
    else:
        return None  # Return None if the list is empty

# Calculate percentiles
opportunity_median = calculate_percentile(opportunity_times, 50)
case_median = calculate_percentile(case_times, 50)
order_median = calculate_percentile(order_times, 50)

opportunity_80 = calculate_percentile(opportunity_times, 80)
case_80 = calculate_percentile(case_times, 80)
order_80 = calculate_percentile(order_times, 80)

opportunity_90 = calculate_percentile(opportunity_times, 90)
case_90 = calculate_percentile(case_times, 90)
order_90 = calculate_percentile(order_times, 90)

# Print results
print(f"50th percentile (median) for Opportunity: {opportunity_median}")
print(f"50th percentile (median) for Case: {case_median}")
print(f"50th percentile (median) for Order: {order_median}")

print(f"\n80th percentile for Opportunity: {opportunity_80}")
print(f"80th percentile for Case: {case_80}")
print(f"80th percentile for Order: {order_80}")

print(f"\n90th percentile for Opportunity: {opportunity_90}")
print(f"90th percentile for Case: {case_90}")
print(f"90th percentile for Order: {order_90}")
