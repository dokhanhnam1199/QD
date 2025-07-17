import os
import glob
from omegaconf import OmegaConf
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

def filter_traceback(stdout_str):
    if "Traceback" in stdout_str:
        return "error"
    return ""

def read_bd_values_from_stdout(folder, bd_list, bd_step):
    bd_arrays = {bd: [] for bd in bd_list}
    for stdout_filepath in sorted(glob.glob(os.path.join(folder, "*.txt_stdout.txt"))):
        with open(stdout_filepath, 'r') as f:
            stdout_str = f.read()
        traceback_msg = filter_traceback(stdout_str)
        if traceback_msg == '':
            try:
                lines = stdout_str.strip().split('\n')
                l = len(bd_list)
                for i, bd in enumerate(bd_list):
                    val = float(lines[-l + i])
                    bd_arrays[bd].append(val)
            except Exception as e:
                print(f"Error parsing {stdout_filepath}: {e}")
        else:
            print(f"Error in {stdout_filepath}: {traceback_msg}")
    return bd_arrays

if __name__ == "__main__":
    # Load bd_list and bd_step from config.yaml
    config = OmegaConf.load("cfg/config.yaml")
    bd_list = config.bd_list
    bd_step = config.bd_step

    # Define which are "integer-like"
    int_metrics = {"SLOC", "cyclomatic_complexity", "token_count"}

    # Loop over each folder in outputs/main
    for folder in sorted(glob.glob("outputs/main/*")):
        if not os.path.isdir(folder):
            continue

        folder_name = os.path.basename(folder)
        dist_folder = os.path.join("bd_analyze", folder_name)
        os.makedirs(dist_folder, exist_ok=True)

        bd_arrays = read_bd_values_from_stdout(folder, bd_list, bd_step)

        for bd in bd_list:
            plt.figure()
            data = bd_arrays[bd]
            if bd in int_metrics:
                unique_vals, counts = np.unique(data, return_counts=True)
                plt.bar(unique_vals, counts, color='skyblue', edgecolor='black')
                plt.title(f"{folder_name}")
                plt.ylabel("Frequency")
            else:
                sns.kdeplot(bd_arrays[bd], fill=True)
                plt.title(f"{folder_name}")
                plt.ylabel("Density")

            plt.xlabel(f"{bd} value")
            plt.grid(True, linestyle='--', alpha=0.7)
            plt.tight_layout()
            plt.savefig(os.path.join(dist_folder, f"{bd}_distribution.png"))
            plt.close()

        print(f"Plots saved as PNG files in {dist_folder}.")
