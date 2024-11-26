import matplotlib.pyplot as plt
from collections import Counter
def weighted_mean_subtract_min(counts):
    weighted_sum = sum(key * weight for key, weight in counts.items())
    total_weight = sum(weight for weight in counts.values())
    weighted_mean = weighted_sum / total_weight
    min_key = min(counts.keys())
    
    return weighted_mean - min_key

def draw_plots(arrival_times_list, arrival_time_time, arrival_time_arrival, flow_rate, frame_density):
    # Count the frequency of each integer for the bar plot
    counts = Counter(arrival_times_list)
    values, frequencies = zip(*counts.items())

    # Create subplot 1 for the bar plot
    plt.subplot(2, 2, 1)  # 1 row, 2 columns, subplot 1
    plt.bar(values, frequencies)
    plt.xlabel('Travel time (frames)')
    plt.ylabel('Count')
    plt.title('Travel times')

    # Create subplot 2 for the line plot
    plt.subplot(2, 2, 2)  # 1 row, 2 columns, subplot 2
    plt.plot(arrival_time_time, arrival_time_arrival, marker='.', linestyle='None')
    plt.xlabel('Simulation time (frames)')
    plt.ylabel('Average arrival time (frames)')
    plt.title('Average arrival time against time of arrival')

    # Create subplot 2 for the line plot
    plt.subplot(2, 2, 3)  # 1 row, 2 columns, subplot 2
    x_values, y_values = zip(*flow_rate)
    plt.plot(x_values, y_values, marker='.', linestyle='None')
    plt.xlabel('Simulation time (frames)')
    plt.ylabel('Averge velocity (cells/frames)')
    plt.title('flow rate')

    # Create subplot 2 for the line plot
    plt.subplot(2, 2, 4)  # 1 row, 2 columns, subplot 2
    x_values, y_values = zip(*frame_density)
    plt.plot(x_values, y_values, marker='.', linestyle='None')
    plt.xlabel('Simulation time (frames)')
    plt.ylabel('Car density (cars/cells)')
    plt.title('Car density over time')

    # printing interesting results
    print('Average time in traffic (frames):', weighted_mean_subtract_min(counts))

    # Adjust layout to prevent overlapping
    plt.tight_layout()

    # Show the plots
    plt.show()
