import os
import glob
import json
import matplotlib.pyplot as plt
from omegaconf import OmegaConf
import math

# Your BD configuration
config = OmegaConf.load("cfg/config.yaml")
bd_list = config.bd_list
bd_step = config.bd_step

main_dir = "outputs/main"

def compute_bd_ranges_and_bins(population, bd_list, bd_step):
    bd_min = {bd: float('inf') for bd in bd_list}
    bd_max = {bd: float('-inf') for bd in bd_list}

    for individual in population:
        for i, bd in enumerate(bd_list):
            val = individual.get(bd)
            if val is not None:
                bd_min[bd] = min(bd_min[bd], val)
                bd_max[bd] = max(bd_max[bd], val)

    bd_ranges = {bd: (bd_min[bd], bd_max[bd]) for bd in bd_list}
    possible_bins = 1
    for i, bd in enumerate(bd_list):
        min_v, max_v = bd_ranges[bd]
        if min_v == float('inf') or max_v == float('-inf'):
            n_bins = 1
        else:
            n_bins = int((max_v - min_v) // bd_step[i]) + 1
        possible_bins *= n_bins

    return bd_ranges, possible_bins

# Loop through each experiment folder
for folder in sorted(glob.glob(os.path.join(main_dir, "*"))):
    if not os.path.isdir(folder):
        continue

    folder_name = os.path.basename(folder)
    analyze_folder = os.path.join("bd_analyze", folder_name)
    os.makedirs(analyze_folder, exist_ok=True)

    population_bins = []
    iterations = []
    max_bins_list = []
    density_ratios = []
    avg_objectives = []

    # Process each iteration JSON
    for json_file in sorted(glob.glob(os.path.join(folder, "population_iter*.json"))):
        iter_num = int(os.path.splitext(os.path.basename(json_file))[0].split("population_iter")[1])

        with open(json_file, 'r') as f:
            population = json.load(f)

        # Count unique BD bins (tuples of bd values divided by bd_step)
        unique_bins = set()
        for individual in population:
            try:
                bin_tuple = tuple(
                    int(individual.get(bd, 0) // bd_step[i])
                    for i, bd in enumerate(bd_list)
                )
                unique_bins.add(bin_tuple)
            except Exception:
                continue
        n_bins = len(unique_bins)
        bd_ranges, max_possible_bins = compute_bd_ranges_and_bins(population, bd_list, bd_step)

        # Calculate average objective
        total_obj = 0
        count = 0
        for individual in population:
            obj = individual.get("obj")
            if obj is not None and math.isfinite(obj):
                total_obj += obj
                count += 1
        avg_obj = total_obj / count if count > 0 else 0

        iterations.append(iter_num)
        population_bins.append(n_bins)
        max_bins_list.append(max_possible_bins)
        density_ratios.append(n_bins / max_possible_bins if max_possible_bins > 0 else 0)
        avg_objectives.append(avg_obj)

    if iterations:
        # Combined Plot: Unique BD Bins + Avg Objective
        fig, ax1 = plt.subplots(figsize=(8, 5))

        sorted_pop_pairs = sorted(zip(iterations, population_bins))
        sorted_iters_pop, sorted_population_bins = zip(*sorted_pop_pairs)

        ax1.bar(sorted_iters_pop, sorted_population_bins, color='mediumslateblue', edgecolor='black')
        ax1.set_xlabel("Iteration")
        ax1.set_ylabel("Bins", color='mediumslateblue')
        ax1.tick_params(axis='y', labelcolor='mediumslateblue')
        ax1.grid(True, axis='y', linestyle='--', alpha=0.6)

        # Set y-axis to integer ticks only
        from matplotlib.ticker import MaxNLocator
        ax1.yaxis.set_major_locator(MaxNLocator(integer=True))

        # Add second y-axis for average objective
        ax2 = ax1.twinx()
        sorted_obj_pairs = sorted(zip(iterations, avg_objectives))
        sorted_iters_obj, sorted_avg_objectives = zip(*sorted_obj_pairs)
        for i, obj in sorted_obj_pairs:
            print(f"Iteration {i}: avg objective = {obj}")
        ax2.plot(sorted_iters_obj, sorted_avg_objectives, color='crimson', marker='o', linestyle='-')
        ax2.set_ylabel("Average Objective", color='crimson')
        ax2.tick_params(axis='y', labelcolor='crimson')

        plt.title(f"{folder_name} - Bins and Avg Objective")
        plt.tight_layout()
        pop_obj_plot_path = os.path.join(analyze_folder, f"population.png")
        plt.savefig(pop_obj_plot_path)
        plt.close()
        print(f"Saved bins + objective plot to {pop_obj_plot_path}")

        # Plot density ratio as line
        sorted_pairs = sorted(zip(iterations, density_ratios))
        sorted_iterations, sorted_density_ratios = zip(*sorted_pairs)
        plt.figure(figsize=(8, 5))
        plt.plot(sorted_iterations, sorted_density_ratios, marker='o', linestyle='-', color='darkgreen')
        plt.title(f"{folder_name} - Density Ratio")
        plt.xlabel("Iteration")
        plt.ylabel("Filled bins / Max possible bins")
        plt.grid(True, linestyle='--', alpha=0.6)
        plt.tight_layout()
        density_plot_path = os.path.join(analyze_folder, f"density_ratio.png")
        plt.savefig(density_plot_path)
        plt.close()
        print(f"Saved density ratio plot to {density_plot_path}")

    # Save a small summary file
    summary_path = os.path.join(analyze_folder, f"bd_summary.txt")
    with open(summary_path, "w") as f:
        for it, n_bins, bins, ratio, avg_obj in zip(iterations, population_bins, max_bins_list, density_ratios, avg_objectives):
            f.write(f"Iteration {it}: unique_bd_bins={n_bins}, max_possible_bins={bins}, density={ratio:.4f}, avg_objective={avg_obj:.4f}\n")
    print(f"Saved summary to {summary_path}")
