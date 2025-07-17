import os
import glob
import json
import matplotlib.pyplot as plt

# Your BD configuration
bd_list = ["SLOC", "cyclomatic_complexity", "halstead", "mi", "token_count"]
bd_step = [3, 1, 50, 5, 30]

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

    population_sizes = []
    iterations = []
    max_bins_list = []
    density_ratios = []

    # Process each iteration JSON
    for json_file in sorted(glob.glob(os.path.join(folder, "population_iter*.json"))):
        iter_num = int(os.path.splitext(os.path.basename(json_file))[0].split("population_iter")[1])
        
        with open(json_file, 'r') as f:
            population = json.load(f)

        pop_size = len(population)
        bd_ranges, max_possible_bins = compute_bd_ranges_and_bins(population, bd_list, bd_step)

        iterations.append(iter_num)
        population_sizes.append(pop_size)
        max_bins_list.append(max_possible_bins)
        
        # Avoid division by zero
        ratio = pop_size / max_possible_bins if max_possible_bins > 0 else 0
        density_ratios.append(ratio)


    if iterations:
        # Plot population size as bars
        plt.figure(figsize=(8,5))
        plt.bar(iterations, population_sizes, color='mediumslateblue', edgecolor='black')
        plt.title(f"{folder_name}")
        plt.xlabel("Iteration")
        plt.ylabel("Number of bins")
        plt.grid(True, axis='y', linestyle='--', alpha=0.6)
        plt.tight_layout()
        pop_plot_path = os.path.join(analyze_folder, f"population.png")
        plt.savefig(pop_plot_path)
        plt.close()
        print(f"Saved population bar plot to {pop_plot_path}")

        # Plot density ratio as line
        sorted_pairs = sorted(zip(iterations, density_ratios))
        sorted_iterations, sorted_density_ratios = zip(*sorted_pairs)
        plt.figure(figsize=(8,5))
        plt.plot(sorted_iterations, sorted_density_ratios, marker='o', linestyle='-', color='darkgreen')
        plt.title(f"{folder_name}")
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
        for it, size, bins, ratio in zip(iterations, population_sizes, max_bins_list, density_ratios):
            f.write(f"Iteration {it}: population={size}, max_possible_bins={bins}, density={ratio:}\n")
    print(f"Saved summary to {summary_path}")
