import json
from typing import List, Tuple, Any
import matplotlib.pyplot as plt
import os

def find_experiment_results_by_keyword(keyword: str):
    with open('nearest_objs_results.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    results = {}
    for k, v in data.items():
        if keyword in k:
            results[k] = v
    return results

def plot_comparison(results, qd_results):
    keys = list(results.keys())
    qd_keys = list(qd_results.keys())
    assert len(keys) == 3 and len(qd_keys) == 3, "Both dicts must have exactly 3 entries."
    fig, axes = plt.subplots(1, 3, figsize=(18, 5), sharey=False)
    all_lines = []
    all_labels = []
    for i, key in enumerate(keys):
        ax = axes[i]
        # Get data for results
        arr = results[key]
        tokens = [row[0] for row in arr]
        best_obj = [row[1] for row in arr]
        swdi = [row[2] for row in arr]
        cdi = [row[3] for row in arr]
        # Get data for qd_results (match by index)
        qd_arr = qd_results[qd_keys[i]]
        qd_tokens = [row[0] for row in qd_arr]
        qd_best_obj = [row[1] for row in qd_arr]
        qd_swdi = [row[2] for row in qd_arr]
        qd_cdi = [row[3] for row in qd_arr]
        # Shorten key names for legend
        short_key = key.split('_')[0]
        short_qd_key = qd_keys[i].split('_')[0]
        l1, = ax.plot(tokens, best_obj, label=f'{short_key} best objective', color='tab:blue')
        l2, = ax.plot(qd_tokens, qd_best_obj, label=f'{short_qd_key} best objective', color='tab:blue', linestyle='dotted')
        ax.set_xlabel('Token')
        ax.tick_params(axis='y', labelcolor='tab:blue')
        ax2 = ax.twinx()
        l3, = ax2.plot(tokens, swdi, label=f'{short_key} swdi', color='tab:orange')
        l4, = ax2.plot(tokens, cdi, label=f'{short_key} cdi', color='tab:green')
        l5, = ax2.plot(qd_tokens, qd_swdi, label=f'{short_qd_key} swdi', color='tab:orange', linestyle='dotted')
        l6, = ax2.plot(qd_tokens, qd_cdi, label=f'{short_qd_key} cdi', color='tab:green', linestyle='dotted')
        ax2.tick_params(axis='y', labelcolor='tab:orange')
        ax.set_title(key)
        # Only collect legend handles/labels from the first chart
        if i == 0:
            lines, labels = ax.get_legend_handles_labels()
            lines2, labels2 = ax2.get_legend_handles_labels()
            all_lines = lines + lines2
            all_labels = labels + labels2
    # Place a single legend for all charts in the center top
    fig.legend(all_lines, all_labels, loc='upper center', ncol=3, fontsize='small')
    plt.tight_layout(rect=(0, 0, 1, 0.93))
    # Save the chart with filename = charts/algorithm_problem.png (from the first key)
    save_dir = 'charts'
    os.makedirs(save_dir, exist_ok=True)
    filename = os.path.join(save_dir, f"{algorithm}_{problem}.png")
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    # plt.show()

# Example usage:
# with open('results.json') as f:
#     results = json.load(f)
# with open('qd_results.json') as f:
#     qd_results = json.load(f)
# plot_comparison(results, qd_results)

if __name__ == "__main__":
    problem = 'tsp_aco'
    algorithm = 'reevo'
    results = find_experiment_results_by_keyword(algorithm+'_'+problem)
    qd_results = find_experiment_results_by_keyword(algorithm+'-qd_'+problem)
    plot_comparison(results, qd_results)
