import pandas as pd
import glob
import numpy as np
from collections import Counter

def running_stats():
    counts = Counter()
    total_count = 0
    min_val = float('inf')
    max_val = float('-inf')
    sum_vals = 0
    
    # First pass - build histogram and basic stats
    for fail in glob.glob("/data/bussid_STOPPED_AT_staatusega_2023/*.csv"):
        for chunk in pd.read_csv(fail, usecols=['distance_from_stop_meters'], chunksize=10000):
            valid_values = chunk['distance_from_stop_meters'].dropna()
            valid_values = valid_values[valid_values >= 0]
            
            if len(valid_values) > 0:
                # Update histogram with rounded values (0.1m precision)
                for val in valid_values:
                    counts[round(val, 1)] += 1
                
                min_val = min(min_val, valid_values.min())
                max_val = max(max_val, valid_values.max())
                sum_vals += valid_values.sum()
                total_count += len(valid_values)
    
    if total_count == 0:
        return None
        
    # Calculate quartiles from histogram
    sorted_values = sorted(counts.items())
    running_count = 0
    Q1 = Q3 = None
    Q1_target = total_count // 4
    Q3_target = (total_count * 3) // 4
    
    for value, count in sorted_values:
        running_count += count
        if Q1 is None and running_count >= Q1_target:
            Q1 = value
        if running_count >= Q3_target:
            Q3 = value
            break
    
    IQR = Q3 - Q1
    cutoff = Q3 + 2.0 * IQR
    
    # Count points below cutoff using histogram
    below_cutoff = sum(count for value, count in counts.items() if value <= cutoff)
    
    mean = sum_vals / total_count
    
    return {
        'min': min_val,
        'max': max_val,
        'mean': mean,
        'Q1': Q1,
        'Q3': Q3,
        'IQR': IQR,
        'cutoff': cutoff,
        'total_count': total_count,
        'below_cutoff': below_cutoff
    }

# Calculate statistics
stats = running_stats()

if stats:
    print(f"\nStatistika kauguste kohta (meetrites):")
    print(f"Minimaalne: {stats['min']:.2f}")
    print(f"Maksimaalne: {stats['max']:.2f}")
    print(f"Keskmine: {stats['mean']:.2f}")
    print(f"Q1 (25%): {stats['Q1']:.2f}")
    print(f"Q3 (75%): {stats['Q3']:.2f}")
    print(f"IQR: {stats['IQR']:.2f}")
    print(f"Soovituslik cutoff punkt (iIQR meetodiga): {stats['cutoff']:.2f}")
    print(f"Kehtivaid andmepunkte kokku: {stats['total_count']}")
    print(f"Andmepunkte alla cutoff punkti: {stats['below_cutoff']}")
    print(f"Protsent andmeid alla cutoff punkti: {(stats['below_cutoff'] / stats['total_count'] * 100):.2f}%")
else:
    print("Andmeid ei leitud või kõik väärtused olid kehtetud")